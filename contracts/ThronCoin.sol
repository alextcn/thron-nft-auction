// SPDX-License-Identifier: MIT

pragma solidity 0.8.6;

import "@openzeppelin/contracts/token/ERC20/presets/ERC20PresetMinterPauser.sol";

/// @notice this is mock contract for Throne payable token. Use it for testnet and unittests only.
contract ThronCoin is ERC20PresetMinterPauser {
    constructor() ERC20PresetMinterPauser("ThroneCoin", "THN") {}

    function name() public view virtual override returns (string memory) {
        return "Throne";
    }  //todo redeploy to ropsten with correct constructor argument
}
