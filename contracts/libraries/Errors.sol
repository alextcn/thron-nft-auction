// SPDX-License-Identifier: agpl-3.0
pragma solidity 0.8.6;


// Contains error code strings

library Errors {
  string public constant INVALID_AUCTION_PARAMS = 'INVALID_AUCTION_PARAMS';
  string public constant INVALID_ETHER_AMOUNT = 'INVALID_ETHER_AMOUNT';
  string public constant AUCTION_EXISTS = 'AUCTION_EXISTS';
  string public constant AUCTION_NOT_FINISHED = 'AUCTION_NOT_FINISHED';
  string public constant AUCTION_FINISHED = 'AUCTION_FINISHED';
  string public constant SMALL_BID_AMOUNT = 'SMALL_BID_AMOUNT';
  string public constant PAUSED = 'PAUSED';
  string public constant NO_RIGHTS = 'NO_RIGHTS';
  string public constant NOT_ADMIN = 'NOT_ADMIN';
  string public constant EMPTY_WINNER = 'EMPTY_WINNER';
  string public constant AUCTION_ALREADY_STARTED = 'AUCTION_ALREADY_STARTED';
  string public constant AUCTION_NOT_EXISTS = 'AUCTION_NOT_EXISTS';
  string public constant NFT_CONTRACT_IS_NOT_ALLOWED = 'NFT_CONTRACT_IS_NOT_ALLOWED';
  string public constant ZERO_ADDRESS = 'ZERO_ADDRESS';
}
