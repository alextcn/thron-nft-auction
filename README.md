# CUSTOM

## env
```bash
INSTAGRAM_REDIRECT_URI
INSTAGRAM_CLIENT_ID
INSTAGRAM_CLIENT_SECRET
```

```bash
run develop
docker-compose --env-file=.env.backend -f docker-compose.yaml -f docker-compose.ganache.yaml -f docker-compose.pg-port.yaml up -d

docker-compose --env-file=.env.backend -f docker-compose.yaml -f docker-compose.ganache.yaml -f docker-compose.pg-port.yaml restart

run demo
docker-compose --env-file=.env.backend -f docker-compose.yaml up -d

./dc.sh exec app python manage.py makemigrations
./dc.sh exec app python manage.py migrate

```

```bash
brownie pm install "OpenZeppelin/openzeppelin-contracts@4.1.0"
brownie pm install "OpenZeppelin/openzeppelin-contracts-upgradeable@4.1.0"
```

```bash
brownie networks add live truffledev host=https://127.0.0.1:9545 chainid=1337

???
brownie networks add live nftdev host=http://127.0.0.1:8545 chainid=1338

brownie accounts new nftdev_1

brownie run deploy.py --network nftdev
brownie run deploy.py --network ropsten

```


```bash
brownie compile
cp -r build/contracts/* ./nft_auction_backend/web3proxy/abi/
cp -r build/contracts/* ./src/config/constants/abi/

# pass: 12341234
brownie run deploy.py --network nftdev
```



## BackEnd

```bash
virtualenv -p python3.8 venv
. venv/bin/activate
pip install -r requirements.txt

python manage.py runserver 0.0.0.0:8000
```

## Frontend

check .env

```
npm install
npm run build
npm run deploy
```
