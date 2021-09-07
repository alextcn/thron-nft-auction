// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/IERC721TokenAuthor.sol";

/**
 * @dev Implementation of https://eips.ethereum.org/EIPS/eip-721[ERC721] Non-Fungible Token Standard, including
 * the Metadata URI extension.
 */
contract ThronNFT is ERC721, ERC721Enumerable, ERC721URIStorage, Ownable, IERC721TokenAuthor {
    uint256 public nextTokenId = 0;
    mapping (uint256 => address) private _tokenAuthor;

    constructor() ERC721("ThroneNFT", "THNNFT") {}

    function mintWithTokenURI(string memory _tokenURI) public returns (uint256) {
        require(bytes(_tokenURI).length > 0, "EMPTY_METADATA");
        uint256 tokenId = nextTokenId++;
        _mintWithTokenURI(_msgSender(), tokenId, _tokenURI);
        return tokenId;
    }

    /**
     * @dev I'm not sure if we need this method. It would be OK to have it for post-moderation (e.g. inappropriate url).
     */
    function burn(uint256 tokenId) public {
        require(ERC721.ownerOf(tokenId) == msg.sender, "NOT_OWNER");
        _burn(tokenId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function _mintWithTokenURI(address to, uint256 tokenId, string memory _tokenURI) internal virtual {
        _mint(to, tokenId);
        _setTokenURI(tokenId, _tokenURI);
    }

    function _mint(address to, uint256 tokenId) internal override {
        super._mint(to, tokenId);  // take care about multiple inheritance
        _tokenAuthor[tokenId] = to;
    }

    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);  // take care about multiple inheritance
        delete _tokenAuthor[tokenId];
    }

    function tokenAuthor(uint256 tokenId) external override view returns(address) {
        require(_exists(tokenId), "query for nonexistent token");
        return _tokenAuthor[tokenId];
    }

    function _beforeTokenTransfer(address from, address to, uint256 tokenId) internal override(ERC721, ERC721Enumerable) {
        ERC721Enumerable._beforeTokenTransfer(from, to, tokenId);
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721Enumerable) returns (bool) {
        return interfaceId == type(IERC721TokenAuthor).interfaceId
            || super.supportsInterface(interfaceId);
    }
}
