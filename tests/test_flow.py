import brownie

from nft_auction_backend.web3proxy.const import ADDRESS_ZERO
from brownie.convert import Fixed
from brownie import Auction


def test_revision(auction):
    rev = auction.getRevision()
    expected = 7
    assert rev == expected, f'wrong auction version is tested, actual'


def test_empty_metadata_minting_fails(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    with brownie.reverts("EMPTY_METADATA"):
        throne_nft.mintWithTokenURI("", {'from': minter})


def test_incorrect_nfthub(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    with brownie.reverts("NFT_CONTRACT_IS_NOT_ALLOWED"):
        some_wrong_address = users[-1]
        auction.createAuction(some_wrong_address, nft_id, start_price, {'from': minter})


def test_incorrect_startprice(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('0 ether')
    with brownie.reverts("INVALID_AUCTION_PARAMS"):
        auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})


def test_normal_flow(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    # approve for bid = reserve price
    bid_price = start_price
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    # claim
    auction.claimWonNFT(throne_nft.address, nft_id, {'from': claimer})

    assert throne_nft.ownerOf(nft_id) == bidder


def test_claim_empty_winner(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    with brownie.reverts('EMPTY_WINNER'):
        auction.claimWonNFT(throne_nft.address, nft_id, {'from': claimer})


def test_bid_by_auctioneer(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = minter  # <- take a look here
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {
        'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter, 'startPrice': start_price}

    # approve for bid = reserve price
    bid_price = start_price
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    # claim
    auction.claimWonNFT(throne_nft.address, nft_id, {'from': claimer})

    assert throne_nft.ownerOf(nft_id) == bidder


def test_normal_flow_claim_by_winner(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})

    # approve for bid = reserve price
    bid_price = Fixed('1 ether')
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    # claim
    auction.claimWonNFT(throne_nft.address, nft_id, {'from': claimer})

    assert throne_nft.ownerOf(nft_id) == bidder


def test_normal_flow_claim_by_admin(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = admin

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})

    # approve for bid = reserve price
    bid_price = Fixed('1 ether')
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    # claim
    auction.claimWonNFT(throne_nft.address, nft_id, {'from': claimer})

    assert throne_nft.ownerOf(nft_id) == bidder


def test_normal_flow_claim_by_auctioneer(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = minter

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})

    # approve for bid = reserve price
    bid_price = Fixed('1 ether')
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    # claim
    auction.claimWonNFT(throne_nft.address, nft_id, {'from': claimer})

    assert throne_nft.ownerOf(nft_id) == bidder


def test_normal_flow_claim_by_other_user(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = users[2]

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})

    # approve for bid = reserve price
    bid_price = Fixed('1 ether')
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    # claim
    auction.claimWonNFT(throne_nft.address, nft_id, {'from': claimer})

    assert throne_nft.ownerOf(nft_id) == bidder


def test_end_timestamp_correct_on_start(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = users[2]

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})

    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    assert end_timestamp == 0

    # approve for bid = reserve price
    bid_price = Fixed('1 ether')
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    tx = auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    assert tx.events['BidSubmitted']['endTimestamp'] == chain[-1]['timestamp'] + auction.auctionDuration()


def test_end_timestamp_correct_after_overtime(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = users[2]

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})

    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    assert end_timestamp == 0

    # approve for bid = reserve price
    bid_price = start_price
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    tx = auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})
    assert tx.events['BidSubmitted']['endTimestamp'] == chain[-1]['timestamp'] + auction.auctionDuration()

    # travel to the future (but not finished)
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() - 10)
    chain.mine()

    bid2_price = int(bid_price * 105 // 100)
    throne_coin.approve(auction.address, bid2_price - bid_price, {'from': bidder})
    tx = auction.bid(throne_nft.address, nft_id, bid2_price, {'from': bidder})
    assert tx.events['BidSubmitted']['endTimestamp'] == chain[-1]['timestamp'] + auction.overtimeWindow()


def test_failed_to_place_bid_on_finished(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = users[2]

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})

    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    assert end_timestamp == 0

    # approve for bid = reserve price
    bid_price = Fixed('1 ether')
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    tx = auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})
    assert tx.events['BidSubmitted']['endTimestamp'] == chain[-1]['timestamp'] + auction.auctionDuration()

    # travel to the future (make finished)
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    with brownie.reverts('AUCTION_FINISHED'):
        bid2_price = bid_price * 105 / Fixed(100)
        auction.bid(throne_nft.address, nft_id, bid2_price, {'from': bidder})


def test_change_reserve_price(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price1 = Fixed('0.9 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price1, {'from': minter})
    assert tx.events['AuctionCreated']['startPrice'] == start_price1

    # change reserve price
    start_price2 = Fixed('1 ether')
    tx = auction.changeReservePrice(throne_nft.address, nft_id, start_price2, {'from': minter})
    assert tx.events['ReservePriceChanged']['startPrice'] == start_price2

    # approve for bid = reserve price
    bid_price = start_price2
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    # claim
    auction.claimWonNFT(throne_nft.address, nft_id, {'from': claimer})

    assert throne_nft.ownerOf(nft_id) == bidder


def test_change_reserve_price_after_bid(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price1 = Fixed('0.9 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price1, {'from': minter})
    assert tx.events['AuctionCreated']['startPrice'] == start_price1

    # approve for bid = reserve price
    bid_price = start_price1
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # change reserve price
    start_price2 = Fixed('1 ether')
    with brownie.reverts('AUCTION_ALREADY_STARTED'):
        auction.changeReservePrice(throne_nft.address, nft_id, start_price2, {'from': minter})


def test_change_reserve_price_wrong_value(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price1 = Fixed('0.9 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price1, {'from': minter})
    assert tx.events['AuctionCreated']['startPrice'] == start_price1

    # change reserve price
    start_price2 = Fixed('0 ether')
    with brownie.reverts('INVALID_AUCTION_PARAMS'):
        auction.changeReservePrice(throne_nft.address, nft_id, start_price2, {'from': minter})


def test_change_reserve_price_by_admin(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price1 = Fixed('0.9 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price1, {'from': minter})
    assert tx.events['AuctionCreated']['startPrice'] == start_price1

    # change reserve price by admin works
    start_price2 = Fixed('1 ether')
    tx = auction.changeReservePrice(throne_nft.address, nft_id, start_price2, {'from': admin})
    assert tx.events['ReservePriceChanged']['startPrice'] == start_price2


def test_change_reserve_price_by_other_user(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price1 = Fixed('0.9 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price1, {'from': minter})
    assert tx.events['AuctionCreated']['startPrice'] == start_price1

    # change reserve price by admin works
    start_price2 = Fixed('1 ether')
    with brownie.reverts('NO_RIGHTS'):
        auction.changeReservePrice(throne_nft.address, nft_id, start_price2, {'from': users[-1]})


# def test_gas(auction, throne_nft, throne_coin, admin, users, chain):
#     minter = users[0]
#     bidder = users[1]
#
#     # mint
#     tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
#     transfer_event = tx.events["Transfer"]
#     assert transfer_event['from'] == ADDRESS_ZERO
#     assert transfer_event['to'] == minter
#     nft_id = transfer_event['tokenId']
#
#     # approve for auction
#     throne_nft.approve(auction.address, nft_id, {'from': minter})
#
#     # create auction
#     start_price = Fixed('1 ether')
#     tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
#     assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
#                                            'startPrice': start_price}
#
#     # approve for bid = reserve price
#     bid_price = start_price
#     throne_coin.approve(auction.address, bid_price, {'from': bidder})
#
#     # bid1
#     auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})
#
#     # approve for bid2 = reserve price
#     bid2_price = bid_price * Fixed(105) / Fixed(100)
#     throne_coin.approve(auction.address, bid2_price, {'from': bidder})
#
#     # bid2
#     tx1 = auction.bid(throne_nft.address, nft_id, bid2_price, {'from': bidder})
#
#     # approve for bid3 = reserve price
#     bid3_price = bid2_price * Fixed(105) / Fixed(100)
#     throne_coin.approve(auction.address, bid3_price, {'from': bidder})
#
#     # bid3
#     tx2 = auction.bidConst(throne_nft.address, nft_id, bid3_price, {'from': bidder})
#
#     tx1.info()
#     tx2.info()
#     assert 1==0


def test_2_bids(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    bidder2 = users[2]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    # approve for bid = reserve price
    bid_price = start_price
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # approve for bid2 = reserve price
    bid2_price = bid_price * Fixed(105) / Fixed(100)
    throne_coin.approve(auction.address, bid2_price, {'from': bidder2})

    # bid2
    auction.bid(throne_nft.address, nft_id, bid2_price, {'from': bidder2})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    # claim
    auction.claimWonNFT(throne_nft.address, nft_id, {'from': claimer})

    assert throne_nft.ownerOf(nft_id) == bidder2


def test_2_bids_2nd_low(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    bidder2 = users[2]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    # approve for bid = reserve price
    bid_price = start_price
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # approve for bid2 = reserve price
    bid2_price = bid_price * Fixed(105) / Fixed(100) - 1  # low
    throne_coin.approve(auction.address, bid2_price, {'from': bidder2})

    # bid2
    with brownie.reverts('SMALL_BID_AMOUNT'):
        auction.bid(throne_nft.address, nft_id, bid2_price, {'from': bidder2})


def test_2nd_bids_already_finished(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    bidder2 = users[2]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    # approve for bid = reserve price
    bid_price = start_price
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    # approve for bid2 = reserve price
    bid2_price = bid_price * Fixed(105) / Fixed(100)
    throne_coin.approve(auction.address, bid2_price, {'from': bidder2})

    # bid2
    with brownie.reverts('AUCTION_FINISHED'):
        auction.bid(throne_nft.address, nft_id, bid2_price, {'from': bidder2})


def test_10_bids_from_the_same_user(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    bid_price = start_price
    for i in range(10):
        bid_price = bid_price * Fixed(105) / Fixed(100)

        # approve
        throne_coin.approve(auction.address, bid_price, {'from': bidder})

        # bid
        auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    # claim
    auction.claimWonNFT(throne_nft.address, nft_id, {'from': claimer})

    assert throne_nft.ownerOf(nft_id) == bidder


def test_10_bids_from_the_different_users(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    bid_price = start_price
    for i in range(10):
        bidder = users[i % len(users)]
        bid_price = bid_price * Fixed(105) / Fixed(100)

        # approve
        throne_coin.approve(auction.address, bid_price, {'from': bidder})

        # test_royalbid
        auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    # claim
    auction.claimWonNFT(throne_nft.address, nft_id, {'from': bidder})

    assert throne_nft.ownerOf(nft_id) == bidder


def test_royalty(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder1 = users[1]
    bidder2 = users[2]
    claimer1 = bidder1
    claimer2 = bidder2

    # mint
    tx = throne_nft.mintWithTokenURI("https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    # approve for bid = reserve price
    bid_price = start_price
    throne_coin.approve(auction.address, bid_price, {'from': bidder1})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder1})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    # claim
    auction.claimWonNFT(throne_nft.address, nft_id, {'from': claimer1})

    assert throne_nft.ownerOf(nft_id) == bidder1

    # 2nd auction

    # approve for auction
    throne_nft.approve(auction.address, nft_id, {'from': bidder1})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': bidder1})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': bidder1,
                                           'startPrice': start_price}

    # approve for bid = reserve price
    bid_price = start_price
    throne_coin.approve(auction.address, bid_price, {'from': bidder2})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder2})

    # travel to the future
    end_timestamp = auction.getAuctionData(throne_nft.address, nft_id)[3]
    chain.sleep(end_timestamp - chain.time() + 10)
    chain.mine()

    author_throne_balance_before = throne_coin.balanceOf(minter)

    # claim
    auction.claimWonNFT(throne_nft.address, nft_id, {'from': claimer2})

    author_throne_balance_after = throne_coin.balanceOf(minter)

    assert throne_nft.ownerOf(nft_id) == bidder2
    royalty = author_throne_balance_after - author_throne_balance_before
    assert royalty == bid_price * Fixed(1) / Fixed(100)  # royalty = 1%


def test_failed_low_bid(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    claimer = bidder

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    # approve
    bid_price = start_price - Fixed(1)  # small
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    with brownie.reverts('SMALL_BID_AMOUNT'):
        auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})


def test_create_auction_twice_fails(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    with brownie.reverts("AUCTION_EXISTS"):
        auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})


def test_cancel_auction_started_auction_failed(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    # approve
    bid_price = start_price
    throne_coin.approve(auction.address, bid_price, {'from': bidder})
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    with brownie.reverts('AUCTION_ALREADY_STARTED'):
        auction.cancelAuction(throne_nft.address, nft_id, {'from': minter})


def test_cancel_auction(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    tx = auction.cancelAuction(throne_nft.address, nft_id, {'from': minter})
    assert tx.events['AuctionCanceled'] == {'nft': throne_nft.address, 'nftId': nft_id, 'canceler': minter}


def test_cancel_auction_after_change_reserve_price(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    start_price2 = Fixed('2 ether')
    tx = auction.changeReservePrice(throne_nft.address, nft_id, start_price2, {'from': minter})
    assert tx.events['ReservePriceChanged']['startPrice'] == start_price2

    tx = auction.cancelAuction(throne_nft.address, nft_id, {'from': minter})
    assert tx.events['AuctionCanceled'] == {'nft': throne_nft.address, 'nftId': nft_id, 'canceler': minter}


def test_cancel_auction_by_admin(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    tx = auction.cancelAuction(throne_nft.address, nft_id, {'from': admin})
    assert tx.events['AuctionCanceled'] == {'nft': throne_nft.address, 'nftId': nft_id, 'canceler': admin}


def test_cancel_auction_by_someone_else(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    with brownie.reverts('NO_RIGHTS'):
        auction.cancelAuction(throne_nft.address, nft_id, {'from': users[-1]})


def test_cancel_auction_after_bid_failed(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]

    # mint
    tx = throne_nft.mintWithTokenURI(
        "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json", {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    # approve for auction
    tx = throne_nft.approve(auction.address, nft_id, {'from': minter})

    # create auction
    start_price = Fixed('1 ether')
    tx = auction.createAuction(throne_nft.address, nft_id, start_price, {'from': minter})
    assert tx.events['AuctionCreated'] == {'nft': throne_nft.address, 'nftId': nft_id, 'auctioneer': minter,
                                           'startPrice': start_price}

    # approve for bid = reserve price
    bid_price = start_price
    throne_coin.approve(auction.address, bid_price, {'from': bidder})

    # bid
    auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})

    with brownie.reverts('AUCTION_ALREADY_STARTED'):
        auction.cancelAuction(throne_nft.address, nft_id, {'from': minter})


def test_bid_on_nonexistant_auction_failed(auction, throne_nft, throne_coin, admin, users, chain):
    nft_id = 9000
    bid_price = Fixed('1 ether')
    bidder = users[0]
    with brownie.reverts('AUCTION_NOT_EXISTS'):
        auction.bid(throne_nft.address, nft_id, bid_price, {'from': bidder})


def test_cancel_of_nonexistant_auction_failed(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    nft_id = 9000
    with brownie.reverts('AUCTION_NOT_EXISTS'):
        auction.cancelAuction(throne_nft.address, nft_id, {'from': minter})


def test_set_overtime_widnow(auction, admin):
    value = 3600
    tx = auction.setOvertimeWindow(value, {'from': admin})
    assert tx.events['OvertimeWindowSet']['overtimeWindow'] == value


def test_set_overtime_widnow_low(auction, admin):
    with brownie.reverts('INVALID_AUCTION_PARAMS'):
        auction.setOvertimeWindow(59, {'from': admin})


def test_set_overtime_widnow_high(auction, admin):
    with brownie.reverts('INVALID_AUCTION_PARAMS'):
        auction.setOvertimeWindow(365*24*3600+1, {'from': admin})


def test_set_royalty(auction, admin):
    value = 1000  # 10%
    tx = auction.setAuthorRoyaltyNumerator(value, {'from': admin})
    assert tx.events['AuthorRoyaltyNumeratorSet']['authorRoyaltyNumerator'] == value


def test_set_royalty_high(auction, admin):
    value = 10000 + 1  # > 100%
    with brownie.reverts('INVALID_AUCTION_PARAMS'):
        auction.setAuthorRoyaltyNumerator(value, {'from': admin})


def test_set_pricestep(auction, admin):
    value = 1000
    tx = auction.setMinPriceStepNumerator(value, {'from': admin})
    assert tx.events['MinPriceStepNumeratorSet']['minPriceStepNumerator'] == value


def test_set_pricestep_low(auction, admin):
    with brownie.reverts('INVALID_AUCTION_PARAMS'):
        auction.setMinPriceStepNumerator(0, {'from': admin})


def test_set_pricestep_high(auction, admin):
    with brownie.reverts('INVALID_AUCTION_PARAMS'):
        auction.setMinPriceStepNumerator(10000+1, {'from': admin})


def test_set_auctionduration(auction, admin):
    value = 3600
    tx = auction.setAuctionDuration(value, {'from': admin})
    assert tx.events['AuctionDurationSet']['auctionDuration'] == value


def test_set_auctionduration_low(auction, admin):
    with brownie.reverts('INVALID_AUCTION_PARAMS'):
        auction.setAuctionDuration(59, {'from': admin})


def test_set_auctionduration_high(auction, admin):
    with brownie.reverts('INVALID_AUCTION_PARAMS'):
        auction.setAuctionDuration(365*24*3600+1, {'from': admin})


def test_initialize(admin, throne_nft, throne_coin):
    contract = Auction.deploy({'from': admin})
    overtime = 2 * 60  # in prod 15*60
    duration = 5 * 60  # in prod 24*3600
    _minStepNumerator = 500  # 5%
    _authorRoyaltyNumerator = 100  # 1%
    contract.initialize(
        overtime,
        duration,
        _minStepNumerator,
        _authorRoyaltyNumerator,
        throne_coin.address,
        throne_nft.address,
        admin,
    )
    contract.unpause({'from': admin})  # not required when deployed on prod through proxy
    assert contract.getRevision() > 0


def test_initialize_zero_admin(admin, throne_nft, throne_coin):
    contract = Auction.deploy({'from': admin})
    overtime = 2 * 60  # in prod 15*60
    duration = 5 * 60  # in prod 24*3600
    _minStepNumerator = 500  # 5%
    _authorRoyaltyNumerator = 100  # 1%
    with brownie.reverts('ZERO_ADDRESS'):
        contract.initialize(
            overtime,
            duration,
            _minStepNumerator,
            _authorRoyaltyNumerator,
            throne_coin.address,
            throne_nft.address,
            ADDRESS_ZERO,  # admin
        )


def test_initialize_zero_erc721(admin, throne_nft, throne_coin):
    contract = Auction.deploy({'from': admin})
    overtime = 2 * 60  # in prod 15*60
    duration = 5 * 60  # in prod 24*3600
    _minStepNumerator = 500  # 5%
    _authorRoyaltyNumerator = 100  # 1%
    with brownie.reverts('ZERO_ADDRESS'):
        contract.initialize(
            overtime,
            duration,
            _minStepNumerator,
            _authorRoyaltyNumerator,
            throne_coin.address,
            ADDRESS_ZERO,
            admin,
        )


def test_initialize_zero_erc20(admin, throne_nft, throne_coin):
    contract = Auction.deploy({'from': admin})
    overtime = 2 * 60  # in prod 15*60
    duration = 5 * 60  # in prod 24*3600
    _minStepNumerator = 500  # 5%
    _authorRoyaltyNumerator = 100  # 1%
    with brownie.reverts('ZERO_ADDRESS'):
        contract.initialize(
            overtime,
            duration,
            _minStepNumerator,
            _authorRoyaltyNumerator,
            ADDRESS_ZERO,
            throne_nft.address,
            admin,
        )


def test_throne_coin_name(throne_coin):
    assert throne_coin.name() == 'Throne'


def test_throne_coin_symbol(throne_coin):
    assert throne_coin.symbol() == 'THN'


def test_throne_nft_name(throne_nft):
    assert throne_nft.name() == 'ThroneNFT'


def test_throne_nft_symbol(throne_nft):
    assert throne_nft.symbol() == 'THNNFT'


def test_throne_nft_author_for_nonexistent(throne_nft):
    with brownie.reverts('query for nonexistent token'):
        throne_nft.tokenAuthor(9000)


def test_tokenURI(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    uri = "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json"

    # mint
    tx = throne_nft.mintWithTokenURI(uri, {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    assert throne_nft.tokenURI(nft_id) == uri


def test_burn(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    uri = "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json"

    # mint
    tx = throne_nft.mintWithTokenURI(uri, {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    tx = throne_nft.burn(nft_id, {"from": minter})
    assert tx.events['Transfer']['from'] == minter
    assert tx.events['Transfer']['to'] == ADDRESS_ZERO
    assert tx.events['Transfer']['tokenId'] == nft_id


def test_burn_not_owner(auction, throne_nft, throne_coin, admin, users, chain):
    minter = users[0]
    bidder = users[1]
    uri = "https://ipfs.io/ipfs/QmU84SmCFee2ekP7PWpr4zXaqf96jqLQ7oiDR7Qw8qSfiZ/metadata.json"

    # mint
    tx = throne_nft.mintWithTokenURI(uri, {'from': minter})
    transfer_event = tx.events["Transfer"]
    assert transfer_event['from'] == ADDRESS_ZERO
    assert transfer_event['to'] == minter
    nft_id = transfer_event['tokenId']

    with brownie.reverts('NOT_OWNER'):
        throne_nft.burn(nft_id, {"from": users[-1]})


def test_supports_interface(auction, throne_nft, throne_coin, admin, users, chain):
    interface_id = '0xf1e9ff9f'  # type(IERC721TokenAuthor).interfaceId
    assert throne_nft.supportsInterface(interface_id)
