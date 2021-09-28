const { ethers } = require('hardhat')

const NFT_URI = 'empty_uri'


async function mint(nft, toSigner) {
    const tx = await (await nft.connect(toSigner).mintWithTokenURI(NFT_URI)).wait()
    const tokenId = tx.events[0].args['tokenId'].toString()
    console.log(`NFT token ${tokenId} minted to ${toSigner.address}`)
}

async function main() {
    // deploy contract
    const NFT = await ethers.getContractFactory('ThronNFT')
    console.log('Deploying ThronNFT...')
    const nft = await NFT.deploy()
    await nft.deployed()
    console.log('ThronNFT deployed:', nft.address)

    // mint nfts
    const signers = await ethers.getSigners()
    for (const signer of signers) {
        await mint(nft, signer)
    }
}

main()
    .then(() => process.exit(0))
    .catch(error => {
        console.log(error)
        process.exit(1)
})