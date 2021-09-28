const { ethers } = require('hardhat')

const TO = '0xd07dAfB61ebd2de385f01E39D4Bf7785E16554aB'
const NFT_ADDRESS = '0x64a69a381d25271185BDCc9458e3313634880689'
const NFT_URI = 'empty_uri'


async function main() {
    const signer = ethers.provider.getSigner(TO)

    const nft = await ethers.getContractAt('ThronNFT', NFT_ADDRESS)

    const tx = await (await nft.connect(signer).mintWithTokenURI(NFT_URI)).wait()
    const tokenId = tx.events[0].args['tokenId'].toString()
    console.log(`NFT token ${tokenId} minted to ${signer.getAddress()}`)
}

main()
    .then(() => process.exit(0))
    .catch(error => {
        console.log(error)
        process.exit(1)
})