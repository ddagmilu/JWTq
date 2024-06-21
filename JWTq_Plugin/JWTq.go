package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/eclipse/paho.mqtt.golang"
)

// JWTInfo holds the JWT information
type JWTInfo struct {
	Algorithm jwt.SigningMethod
	Key       []byte
	Claims    jwt.MapClaims
}

// ExtractIntFromJSON extracts an integer value from a JSON object
func ExtractIntFromJSON(data map[string]interface{}, key string) int64 {
	if val, ok := data[key].(float64); ok {
		return int64(val)
	}
	return 0
}

// ExtractStringFromJSON extracts a JSON object as a string
func ExtractStringFromJSON(data map[string]interface{}, key string) string {
	if val, ok := data[key]; ok {
		jsonStr, _ := json.Marshal(val)
		return string(jsonStr)
	}
	return ""
}

// MosquittoAuthPlugin struct
type MosquittoAuthPlugin struct{}

// Version returns the plugin version
func (p *MosquittoAuthPlugin) Version() int {
	return mqtt.MOSQ_AUTH_PLUGIN_VERSION
}

// Init initializes the plugin
func (p *MosquittoAuthPlugin) Init(authOpts map[string]string) error {
	return nil
}

// Cleanup cleans up the plugin
func (p *MosquittoAuthPlugin) Cleanup(authOpts map[string]string) error {
	return nil
}

// SecurityInit initializes security
func (p *MosquittoAuthPlugin) SecurityInit(authOpts map[string]string, reload bool) error {
	return nil
}

// SecurityCleanup cleans up security
func (p *MosquittoAuthPlugin) SecurityCleanup(authOpts map[string]string, reload bool) error {
	return nil
}

// UnpwdCheck checks username and password
func (p *MosquittoAuthPlugin) UnpwdCheck(username, password string) error {
	if username == "" || password == "" {
		return fmt.Errorf("authentication failed")
	}

	if username == "jwt" {
		now := time.Now().Unix()
		secretKey := []byte("012345678901234567890123456789AB")

		token, err := jwt.Parse(password, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
			}
			return secretKey, nil
		})

		if err != nil || !token.Valid {
			return fmt.Errorf("authentication failed")
		}

		claims, ok := token.Claims.(jwt.MapClaims)
		if !ok {
			return fmt.Errorf("authentication failed")
		}

		issuedAt := int64(claims["iat"].(float64))
		expiresAt := int64(claims["exp"].(float64))

		if now < issuedAt || now > expiresAt {
			return fmt.Errorf("authentication failed")
		}

		issuer, ok := claims["iss"].(string)
		subject, ok := claims["sub"].(string)
		if !ok || issuer != "trusted_issuer" || subject != "expected_subject" {
			return fmt.Errorf("authentication failed")
		}

		return nil
	}

	return fmt.Errorf("authentication failed")
}

// ACLCheck checks access control list
func (p *MosquittoAuthPlugin) ACLCheck(clientID, username, topic string, access int) error {
	var accessName string
	switch access {
	case mqtt.MOSQ_ACL_NONE:
		accessName = "none"
	case mqtt.MOSQ_ACL_READ:
		accessName = "read"
	case mqtt.MOSQ_ACL_WRITE:
		accessName = "write"
	default:
		return fmt.Errorf("access denied")
	}

	// Debug print
	fmt.Printf("ACL Check: clientID=%s, username=%s, topic=%s, access=%s\n",
		clientID, username, topic, accessName)

	return nil
}

// PSKKeyGet retrieves pre-shared key (not implemented)
func (p *MosquittoAuthPlugin) PSKKeyGet(hint, identity string, key []byte) error {
	return fmt.Errorf("authentication failed")
}

func main() {
	// This is a plugin, so main function is typically empty.
}
