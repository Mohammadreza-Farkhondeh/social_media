package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/gorilla/mux"
	"github.com/gorilla/websocket"
	"github.com/dgrijalva/jwt-go"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var (
	upgrader = websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			origin := r.Header.Get("Origin")
			return origin == "http://127.0.0.1:8080" // or whatever origin you want to allow
		},
	}
	redisDB  *redis.Client
	db       *gorm.DB
	ctx      = context.Background()

)

type Message struct {
	ID        uint   `json:"id"`
	RoomID    uint   `json:"room_id"`
	SenderID  uint   `json:"sender_id"`
	Recipient uint   `json:"recipient"`
	Text      string `json:"text"`
}

type Room struct {
	ID        uint `json:"id"`
	User1ID   uint `json:"user_1_id"`
	User2ID   uint `json:"user_2_id"`
	CreatedAt int64 `json:"created_at"`
	UpdatedAt int64 `json:"updated_at"`
}

type User struct {
    ID        int    `json:"id"`
    Username  string `json:"username"`
    FirstName string `json:"first_name"`
    LastName  string `json:"last_name"`
    Email     string `json:"email"`
}

func main() {
	// Initialize Redis client
	redisDB = redis.NewClient(&redis.Options{
		Addr: "localhost:6379",
	})

	// Initialize PostgreSQL database
	var err error
	db, err = gorm.Open(postgres.Open("host=localhost user=postgresUser password=postgresPassword dbname=postgresDB port=5432 sslmode=disable"), &gorm.Config{})
	if err != nil {
		log.Fatal(err)
	}
	db.AutoMigrate(&Message{})
	db.AutoMigrate(&Room{})

	// Initialize router
	r := mux.NewRouter()
	r.HandleFunc("/ws/{user_id}", handleWebsocket)
	log.Fatal(http.ListenAndServe("0.0.0.0:8080", r))
}

func parseJWT(tokenString string) (int, error) {
    // Parse the JWT token
    token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
        // Check the signing method
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("invalid signing method")
        }

        // Return the secret key used to sign the token
        return []byte("django-insecure-8a28t3qtbu%kj5@*t!_*h%2^r=(pj+!o&*!pcw^u(=+)-bd8fw"), nil
    })
    if err != nil {
        return 0, err
    }

    // Get the user ID from the token claims
    if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
        userID, ok := claims["user_id"].(int)
        if !ok {
            return 0, fmt.Errorf("invalid user ID")
        }
        return userID, nil
    } else {
        return 0, fmt.Errorf("invalid token claims")
    }
}


// func getUserByID(db *gorm.DB, userID int) (*User, error) {
//     // Query the "auth_user" table for the user with the given ID
//     var user User
//     if err := db.First(&user, userID).Error; err != nil {
//         return nil, err
//     }
//     return &user, nil
// }

func handleWebsocket(w http.ResponseWriter, r *http.Request) {
	// Upgrade HTTP connection to WebSocket connection
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println(err)
		return
	}

	// Get user ID from JWT token in request headers
	user1ID, err := parseJWT(r.Header.Get("Authorization"))
	if err != nil {
		log.Println(err)
		conn.Close()
		return
	}

	// Get user ID from URL parameter
	vars := mux.Vars(r)
	user2ID, err := strconv.Atoi(vars["user_id"])
	if err != nil {
		log.Println(err)
		conn.Close()
		return
	}

	// Find the room for this user
	var room Room
	err = db.Where("user_1_id = ? OR user_2_id = ?", user1ID, user2ID).First(&room).Error
	if err != nil {
		// If the room doesn't exist, create a new one
		room = Room{
			User1ID:   uint(user1ID),
			User2ID:   uint(user2ID),
			CreatedAt: now(),
			UpdatedAt: now(),
		}
		err = db.Create(&room).Error
		if err != nil {
			log.Println(err)
			conn.Close()
			return
		}
	}

	// Add client to the Redis channel for this room
	channel := fmt.Sprintf("room_%d", room.ID)
	redisSub := redisDB.Subscribe(ctx, channel)
	

	// Send all messages in the Redis channel to the client
	messages, err := redisDB.LRange(ctx, channel, 0, -1).Result()
	if err != nil {
		log.Println(err)
		conn.Close()
		return
	}
	for _, msg := range messages {
		err = conn.WriteMessage(websocket.TextMessage, []byte(msg))
		if err != nil {
			log.Println(err)
			break
		}
	}

	// Close the Redis subscription when the function returns
	defer func() {
		redisSub.Unsubscribe(ctx, channel)
		redisSub.Close()
		conn.Close()
	}()

	// Continuously read messages from the client
	for {
		_, message, err := conn.ReadMessage()
		if err != nil {
			log.Println(err)
			break
		}

		// Save the message to the database
		msg := Message{
			RoomID:   room.ID,
			SenderID: room.User2ID,
			Recipient: room.User1ID,
			Text:     string(message),
		}
		if user2ID == int(room.User1ID) {
			msg.Recipient = room.User2ID
		}
		err = db.Create(&msg).Error
		if err != nil {
			log.Println(err)
			break
		}

		// Broadcast the message to all clients in the room
		msgJSON, err := json.Marshal(msg)
		if err != nil {
			log.Println(err)
			break
		}
		err = redisDB.RPush(ctx, channel, string(msgJSON)).Err()
		if err != nil {
			log.Println(err)
			break
		}

		// Publish the message to the Redis channel
		err = redisDB.Publish(ctx, channel, string(msgJSON)).Err()
		if err != nil {
			log.Println(err)
			break
		}
	}
}

func now() int64 {
	return time.Now().UnixNano()
}
