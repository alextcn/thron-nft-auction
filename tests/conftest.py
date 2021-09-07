from brownie import ThronCoin, ThronNFT, Auction
import pytest


@pytest.fixture
def admin(accounts):
    return accounts[0]


@pytest.fixture
def users(accounts):
    return accounts[1:]


@pytest.fixture
def throne_coin(accounts, admin):
    contract = ThronCoin.deploy({'from': admin})
    for account in accounts:
        contract.mint(account, 100*1e18, {'from': admin})
    return contract


@pytest.fixture
def throne_nft(admin):
    contract = ThronNFT.deploy({'from': admin})
    return contract


@pytest.fixture
def auction(admin, throne_nft, throne_coin):
    contract = Auction.deploy({'from': admin})
    overtime = 2*60  # in prod 15*60
    duration = 5*60  # in prod 24*3600
    _minStepNumerator = 500  # 5%
    _authorRoyaltyNumerator = 100  # 1%
    contract.initialize(
        overtime,
        duration,
        _minStepNumerator, _authorRoyaltyNumerator, throne_coin.address, throne_nft.address, admin)
    contract.unpause({'from': admin})  # not required when deployed on prod through proxy
    assert not contract.getPaused({'from': admin})
    return contract
