# Safe Space API

## POST /message

Request: { "message": "text", "plugin": "plugin_name" }
Response: { "reply": "text", "crisis": true/false }

## GET /plugins

Returns: list of available backend plugins
