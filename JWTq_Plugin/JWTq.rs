use std::time::{SystemTime, UNIX_EPOCH};
use json::{JsonValue, parse};
use mosquitto_plugin::{MosquittoAuthPlugin, MosquittoAuthResult};
use jwt::{decode, Validation, DecodingKey, TokenData, Algorithm, Header, Claims};

struct JwtInfo {
    algorithm: Algorithm,
    key: Vec<u8>,
    claims: JsonValue,
}

fn extract_json_int(json_obj: &JsonValue, key: &str) -> i64 {
    json_obj[key].as_i64().unwrap_or(0)
}

fn extract_json_string(json_obj: &JsonValue, key: &str) -> Option<String> {
    Some(json_obj[key].dump())
}

struct MyMosquittoPlugin;

impl MosquittoAuthPlugin for MyMosquittoPlugin {
    fn version() -> u32 {
        mosquitto_plugin::MOSQ_AUTH_PLUGIN_VERSION
    }

    fn init(user_data: &mut Option<Box<dyn std::any::Any>>, auth_opts: &[mosquitto_plugin::AuthOpt], auth_opt_count: i32) -> MosquittoAuthResult {
        MosquittoAuthResult::MOSQ_ERR_SUCCESS
    }

    fn cleanup(user_data: &mut Option<Box<dyn std::any::Any>>, auth_opts: &[mosquitto_plugin::AuthOpt], auth_opt_count: i32) -> MosquittoAuthResult {
        MosquittoAuthResult::MOSQ_ERR_SUCCESS
    }

    fn security_init(user_data: &mut Option<Box<dyn std::any::Any>>, auth_opts: &[mosquitto_plugin::AuthOpt], auth_opt_count: i32, reload: bool) -> MosquittoAuthResult {
        MosquittoAuthResult::MOSQ_ERR_SUCCESS
    }

    fn security_cleanup(user_data: &mut Option<Box<dyn std::any::Any>>, auth_opts: &[mosquitto_plugin::AuthOpt], auth_opt_count: i32, reload: bool) -> MosquittoAuthResult {
        MosquittoAuthResult::MOSQ_ERR_SUCCESS
    }

    fn unpwd_check(user_data: &mut Option<Box<dyn std::any::Any>>, username: &str, password: &str) -> MosquittoAuthResult {
        if username.is_empty() || password.is_empty() {
            return MosquittoAuthResult::MOSQ_ERR_AUTH;
        }

        if username == "jwt" {
            let current_time = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs() as i64;
            let key = b"012345678901234567890123456789AB";
            let validation = Validation { leeway: 0, validate_exp: true, algorithms: vec![Algorithm::HS256], validate_nbf: false, aud: None, iss: None, sub: None };

            match decode::<Claims>(password, &DecodingKey::from_secret(key), &validation) {
                Ok(token_data) => {
                    let issued_at = token_data.claims.iat;
                    let expires_at = token_data.claims.exp;

                    if current_time < issued_at || current_time > expires_at {
                        return MosquittoAuthResult::MOSQ_ERR_AUTH;
                    }

                    if token_data.claims.iss != "trusted_issuer" || token_data.claims.sub != "expected_subject" {
                        return MosquittoAuthResult::MOSQ_ERR_AUTH;
                    }

                    MosquittoAuthResult::MOSQ_ERR_SUCCESS
                },
                Err(_) => MosquittoAuthResult::MOSQ_ERR_AUTH,
            }
        } else {
            MosquittoAuthResult::MOSQ_ERR_AUTH
        }
    }

    fn acl_check(user_data: &mut Option<Box<dyn std::any::Any>>, clientid: &str, username: &str, topic: &str, access: i32) -> MosquittoAuthResult {
        let access_name = match access {
            mosquitto_plugin::MOSQ_ACL_NONE => "none",
            mosquitto_plugin::MOSQ_ACL_READ => "read",
            mosquitto_plugin::MOSQ_ACL_WRITE => "write",
            _ => return MosquittoAuthResult::MOSQ_ERR_ACL_DENIED,
        };

        #[cfg(debug_assertions)]
        println!("ACL Check: clientid={}, username={}, topic={}, access={}", clientid, username, topic, access_name);

        MosquittoAuthResult::MOSQ_ERR_SUCCESS
    }

    fn psk_key_get(user_data: &mut Option<Box<dyn std::any::Any>>, hint: &str, identity: &str, key: &mut [u8], max_key_len: i32) -> MosquittoAuthResult {
        MosquittoAuthResult::MOSQ_ERR_AUTH
    }
}

fn main() {
    // This is a plugin, so the main function is typically empty.
}
