#!/bin/bash

# Replace <TOKEN> with the actual token value obtained from login
TOKEN="<TOKEN>"

curl -X GET http://127.0.0.1:8000/api/profile/ \\
  -H "Authorization: Token $TOKEN" \\
  -H "Content-Type: application/json"
