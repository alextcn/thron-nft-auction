const { ethers } = require('hardhat')
const { BigNumber } = require('ethers')

const TOKEN_AMOUNT = 100


async function mint(token, to) {
    const decimals = await token.decimals()
    const tokenAmount = BigNumber.from(TOKEN_AMOUNT).mul(BigNumber.from(10).pow(decimals))
    await (await token.mint(to, tokenAmount)).wait()
    console.log(`minted ${ethers.utils.formatUnits(tokenAmount, decimals)} tokens to ${to}`)
}

async function main() {
    // deploy contract
    const ThronCoin = await ethers.getContractFactory('ThronCoin')
    console.log('Deploying ThronCoin...')
    const coin = await ThronCoin.deploy()
    await coin.deployed()
    console.log('ThronCoin deployed:', coin.address)

    // mint tokens
    const signers = await ethers.getSigners()
    for (const signer of signers) {
        await mint(coin, signer.address)
    }
}

main()
    .then(() => process.exit(0))
    .catch(error => {
        console.log(error)
        process.exit(1)
})