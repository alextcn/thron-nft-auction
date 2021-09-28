// const { ethers } = require("hardhat");

const OVERTIME = 2*60 // in prod 15*60
const MIN_DURATION = 5*60 // in prod 24*3600
const MIN_STEP_NUMERATOR = 500 // 5%
const AUTHOR_ROYALTY_NUMERATOR = 100 // 1%

async function main() {
    deployer = await (await ethers.provider.getSigner()).getAddress()

    const Coin = await ethers.getContractFactory('ThronCoin')
    console.log('Deploying ThronCoin...')
    const coin = await Coin.deploy()
    await coin.deployed()
    console.log('ThronCoin deployed:', coin.address)

    const NFT = await ethers.getContractFactory('ThronNFT')
    console.log('Deploying ThronNFT...')
    const nft = await NFT.deploy()
    await nft.deployed()
    console.log('ThronNFT deployed:', nft.address)

    const Auction = await ethers.getContractFactory('Auction')
    console.log('Deploying Auction...')
    const auction = await Auction.deploy()
    await auction.deployed()
    console.log('Auction deployed:', auction.address)
    console.log('Initializing Auction...')
    await auction.initialize(
        OVERTIME, MIN_DURATION, MIN_STEP_NUMERATOR, AUTHOR_ROYALTY_NUMERATOR,
        coin.address,
        nft.address,
        deployer
    )
    await auction.unpause()
    console.log('Auction initialized')
}

main()
    .then(() => process.exit(0))
    .catch(error => {
        console.log(error)
        process.exit(1)
})