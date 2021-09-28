const { BigNumber } = require('ethers')
const { ethers } = require("hardhat");

const TOKEN_ADDRESS = '0x3baD5566ca28Bc698E9d7F26117Ae9CF268611f0'
const NFT_ADDRESS = '0x64a69a381d25271185BDCc9458e3313634880689'
const AUCTION_ADDRESS = '0x6bBa2E9ec348b66eae13bFa5A79C64CE9e79ac76'

const SLEEP_TIME_MS = 35000


async function main() {
    const signerTokenIds = {
        '0xd07dAfB61ebd2de385f01E39D4Bf7785E16554aB': 3,
        '0x2546BcD3c84621e976D8185a91A922aE77ECEc30': 1,
        '0xbda5747bfd65f08deb54cb465eb87d40e51b197e': 2
    }

    const token = await ethers.getContractAt('ThronCoin', TOKEN_ADDRESS)
    const nft = await ethers.getContractAt('ThronNFT', NFT_ADDRESS)
    const auction = await ethers.getContractAt('Auction', AUCTION_ADDRESS)

    const decimals = await token.decimals()
    const symbol = await token.symbol()

    // 1. create -> bid -> bid -> claim
    let user = ethers.provider.getSigner('0xd07dAfB61ebd2de385f01E39D4Bf7785E16554aB')
    let userAddress = await user.getAddress()
    let nftId = signerTokenIds[userAddress]
    // create
    let startPrice = BigNumber.from(3).mul(BigNumber.from(10).pow(decimals))
    await (await nft.connect(user).approve(auction.address, nftId)).wait()
    await (await auction.connect(user).createAuction(nft.address, nftId, startPrice, false)).wait()
    console.log(`auction created:\nauthor: ${userAddress}\nNFT: [${nft.address}, ${nftId}]\nstart price: ${ethers.utils.formatUnits(startPrice, decimals)} ${symbol}`)
    // bid 1
    user = ethers.provider.getSigner('0x2546BcD3c84621e976D8185a91A922aE77ECEc30')
    userAddress = await user.getAddress()
    let bidAmount = BigNumber.from(4).mul(BigNumber.from(10).pow(decimals))
    await (await token.connect(user).approve(auction.address, bidAmount)).wait()
    await (await auction.connect(user).bid(nft.address, nftId, bidAmount)).wait()
    console.log(`bid ${ethers.utils.formatUnits(bidAmount, decimals)} ${symbol} by ${userAddress}`)
    // bid 2
    user = ethers.provider.getSigner('0xbda5747bfd65f08deb54cb465eb87d40e51b197e')
    userAddress = await user.getAddress()
    bidAmount = BigNumber.from(5).mul(BigNumber.from(10).pow(decimals))
    await (await token.connect(user).approve(auction.address, bidAmount)).wait()
    await (await auction.connect(user).bid(nft.address, nftId, bidAmount)).wait()
    console.log(`bid ${ethers.utils.formatUnits(bidAmount, decimals)} ${symbol} by ${userAddress}`)
    // console.log(`endTimestamp = ${(await auction.getAuctionData(nft.address, nftId)).endTimestamp.toString()}`)
    // wait
    await sleep(SLEEP_TIME_MS)
    // claim
    await (await auction.connect(user).claimWonNFT(nft.address, nftId)).wait()
    console.log(`auction finished, ${userAddress} claimed won NFT`)

    // 2. create -> bid
    user = ethers.provider.getSigner('0x2546BcD3c84621e976D8185a91A922aE77ECEc30')
    userAddress = await user.getAddress()
    nftId = signerTokenIds[userAddress]
    // create
    console.log(`creating an auction...\nauthor: ${userAddress}\tNFT: [${nft.address}, ${nftId}]\nstart price: ${ethers.utils.formatUnits(startPrice, decimals)} ${symbol}`)
    startPrice = BigNumber.from(5).mul(BigNumber.from(10).pow(decimals - 1))
    await (await nft.connect(user).approve(auction.address, nftId)).wait()
    await (await auction.connect(user).createAuction(nft.address, nftId, startPrice, false)).wait()
    console.log(`auction created!`)
    // bid
    user = ethers.provider.getSigner('0xbda5747bfd65f08deb54cb465eb87d40e51b197e')
    userAddress = await user.getAddress()
    bidAmount = BigNumber.from(2).mul(BigNumber.from(10).pow(decimals))
    await (await token.connect(user).approve(auction.address, bidAmount)).wait()
    await (await auction.connect(user).bid(nft.address, nftId, bidAmount)).wait()
    console.log(`bid ${ethers.utils.formatUnits(bidAmount, decimals)} ${symbol} by ${userAddress}`)
    // ... leave onclaimed
    
    // 3. create -> bid -> cancel
    user = ethers.provider.getSigner('0xbda5747bfd65f08deb54cb465eb87d40e51b197e')
    userAddress = await user.getAddress()
    nftId = signerTokenIds[userAddress]
    // create
    user = signers[i]
    startPrice = BigNumber.from(75).mul(BigNumber.from(10).pow(decimals - 2))
    await (await nft.connect(user).approve(auction.address, nftId)).wait()
    await (await auction.connect(user).createAuction(nft.address, nftId, startPrice, false)).wait()
    console.log(`auction created:\nauthor: ${userAddress}\nNFT: [${nft.address}, ${nftId}]\nstart price: ${ethers.utils.formatUnits(startPrice, decimals)} ${symbol}`)
    // cancel
    await (await auction.connect(user).cancelAuction(nft.address, nftId)).wait()
    console.log(`cancelled auction of NFT [${nft.address}, ${nftId}]`)
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

main()
    .then(() => process.exit(0))
    .catch(error => {
        console.log(error)
        process.exit(1)
})