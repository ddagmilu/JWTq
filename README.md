# JWTq: Lightweight JWT mosquitto plugin for Secure and Efficient MQTT Environments

![License](https://img.shields.io/github/license/ddagmilu/JWTq)
![Build Status](https://img.shields.io/github/actions/workflow/status/ddagmilu/JWTq/build.yml)
![Contributors](https://img.shields.io/github/contributors/ddagmilu/JWTq)
![Last Commit](https://img.shields.io/github/last-commit/ddagmilu/JWTq)
![Issues](https://img.shields.io/github/issues/ddagmilu/JWTq)

![JWTq Logo](https://i.imgur.com/tNHj0rA.png) <!-- Placeholder for logo image -->

## Description

JWTq is a lightweight JSON Web Token (JWT) library designed to enhance security and performance in IoT environments using MQTT. Our library focuses on minimizing token size and resource usage while maintaining robust security measures. JWTq is particularly suited for resource-constrained IoT devices that require efficient and secure communication protocols.

## Usage

### AuthServer.py

The `AuthServer.py` serves as the authentication server responsible for issuing, renewing, revoking, and managing JWT tokens. It connects to a MySQL database to store and manage the tokens.

#### Requirements

```python
pip install -r requirements.txt
```

#### Endpoints

- **/token/issue**: Issues a new JWT token.
- **/token/renew**: Renews an existing JWT token.
- **/token/revoke**: Revokes a JWT token.
- **/token/list**: Lists all JWT tokens stored in the database.

#### Example Request

To issue a new token, send a POST request to `/token/issue` with the following JSON payload:
```json
{
  "code": "unique_code",
  "role": "sensor:temperature",
  "messages_class": "default_class",
  "publish_right": true,
  "sub_topic": ["/+/temperature"],
  "pub_topic": ["/sensors/building_1/temp"]
}
```

### JWTq Management Toolkit (main.py)

The JWTq Management Toolkit provides a graphical interface for managing JWT tokens, visualizing MQTT topologies, and integrating terminal functionalities.
Features

![JWTq_Toolkit_Screenshot](https://i.imgur.com/9XlOHFq.png) <!-- Placeholder for logo image -->

