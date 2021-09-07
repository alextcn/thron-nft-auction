// SPDX-License-Identifier: agpl-3.0
pragma solidity 0.8.6;


library DataTypes {
    struct AuctionData {
        uint256 currentBid;
        address auctioneer;
        address currentBidder;
        uint40 endTimestamp;
    }
}
