const { ethers } = require("hardhat");

const TOKEN_ADDRESS = '0x3baD5566ca28Bc698E9d7F26117Ae9CF268611f0'
const NFT_ADDRESS = '0x64a69a381d25271185BDCc9458e3313634880689'

const OVERTIME = 30 // in prod 15*60
const MIN_DURATION = 30 // in prod 24*3600
const MIN_STEP_NUMERATOR = 500 // 5%
const AUTHOR_ROYALTY_NUMERATOR = 100 // 1%

async function main() {
    deployer = await (await ethers.provider.getSigner()).getAddress()

    // deploy
    const Auction = await ethers.getContractFactory('Auction')
    console.log('Deploying Auction...')
    const auction = await Auction.deploy()
    await auction.deployed()
    console.log('Auction deployed:', auction.address)
    console.log('Initializing Auction...')
    await (await auction.initialize(
        OVERTIME, MIN_DURATION, MIN_STEP_NUMERATOR, AUTHOR_ROYALTY_NUMERATOR,
        TOKEN_ADDRESS, NFT_ADDRESS, deployer
    )).wait()
    await (await auction.unpause()).wait()
    console.log('Auction initialized')
}

main()
    .then(() => process.exit(0))
    .catch(error => {
        console.log(error)
        process.exit(1)
})