#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <time.h>
#include <mosquitto.h>
#include <mosquitto_plugin.h>
#include <jansson.h>
#include <jwt.h>

// Plugin version
int mosquitto_auth_plugin_version(void) {
    return MOSQ_AUTH_PLUGIN_VERSION;
}

// Plugin initialization
int mosquitto_auth_plugin_init(void **user_data, struct mosquitto_auth_opt *auth_opts, int auth_opt_count) {
    return MOSQ_ERR_SUCCESS;
}

// Plugin cleanup
int mosquitto_auth_plugin_cleanup(void *user_data, struct mosquitto_auth_opt *auth_opts, int auth_opt_count) {
    return MOSQ_ERR_SUCCESS;
}

// Security initialization
int mosquitto_auth_security_init(void *user_data, struct mosquitto_auth_opt *auth_opts, int auth_opt_count, bool reload) {
    return MOSQ_ERR_SUCCESS;
}

// Security cleanup
int mosquitto_auth_security_cleanup(void *user_data, struct mosquitto_auth_opt *auth_opts, int auth_opt_count, bool reload) {
    return MOSQ_ERR_SUCCESS;
}

// JWT structure
struct jwt {
    jwt_alg_t alg;
    unsigned char *key;
    int key_len;
    json_t *grants;
};

// Get integer from JSON object
static int get_js_int(json_t *js, const char *key) {
    int val = 0;
    json_t *js_val = json_object_get(js, key);
    if (js_val) {
        val = json_integer_value(js_val);
    }
    return val;
}

// Get JSON object as a string
static char *get_js_object(json_t *js, const char *key) {
    size_t flags = JSON_SORT_KEYS | JSON_COMPACT | JSON_ENCODE_ANY;
    char *val = NULL;
    json_t *js_val = json_object_get(js, key);
    if (js_val) {
        val = json_dumps(js_val, flags);
    }
    return val;
}

// Password check with enhanced security constraints
int mosquitto_auth_unpwd_check(void *user_data, const char *username, const char *password) {
    if (username == NULL || password == NULL) {
        return MOSQ_ERR_AUTH;
    }

    jwt_t *jwt = NULL;
    time_t now;
    int iat, exp;
    unsigned char key[32] = "012345678901234567890123456789AB";

    if (strcmp(username, "jwt") == 0) {
        time(&now);

        int status = jwt_decode(&jwt, password, key, sizeof(key));
        if (status == 0 && jwt != NULL) {
            iat = get_js_int(jwt->grants, "iat");
            exp = get_js_int(jwt->grants, "exp");

            if (now < iat || now > exp) {
                jwt_free(jwt);
                return MOSQ_ERR_AUTH;
            }

            // Additional checks on JWT claims (e.g., issuer, subject)
            const char *iss = jwt_get_grant(jwt, "iss");
            const char *sub = jwt_get_grant(jwt, "sub");
            if (iss == NULL || sub == NULL || strcmp(iss, "trusted_issuer") != 0 || strcmp(sub, "expected_subject") != 0) {
                jwt_free(jwt);
                return MOSQ_ERR_AUTH;
            }

            jwt_free(jwt);
            return MOSQ_ERR_SUCCESS;
        }
    }

    return MOSQ_ERR_AUTH;
}

// ACL check
int mosquitto_auth_acl_check(void *user_data, const char *clientid, const char *username, const char *topic, int access) {
    const char *access_name;
    switch (access) {
        case MOSQ_ACL_NONE:
            access_name = "none";
            break;
        case MOSQ_ACL_READ:
            access_name = "read";
            break;
        case MOSQ_ACL_WRITE:
            access_name = "write";
            break;
        default:
            return MOSQ_ERR_ACL_DENIED;
    }

    #ifdef MQAP_DEBUG
    fprintf(stderr, "mosquitto_auth_acl_check: clientid=%s, username=%s, topic=%s, access=%s\n",
            clientid, username, topic, access_name);
    #endif

    return MOSQ_ERR_SUCCESS;
}

// PSK key retrieval (not implemented)
int mosquitto_auth_psk_key_get(void *user_data, const char *hint, const char *identity, char *key, int max_key_len) {
    return MOSQ_ERR_AUTH;
}
