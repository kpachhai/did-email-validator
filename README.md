# Did email validator Rest API

To start, clone did-email-validator repo
```
git clone https://github.com/tuum-tech/did-email-validator.git;
cd did-email-validator;
```

# Prerequisites
- Install required packages[Only needs to be done once]
```
./install.sh
```

# Run
- Copy example environment file
```
cp .env.example .env
```
- Modify .env file with any number of wallets to use
- Start API server
```
./run.sh start
```

# Verify
- To check whether the API is working:
```
curl http://localhost:8081
```
- To validate an email:
```
curl -XPOST -H "Content-Type: application/json" -H "Accept: application/json" -d '{"jwt": "JWT_TOKEN_HERE"}' http://localhost:8081/v1/validation/callback
```