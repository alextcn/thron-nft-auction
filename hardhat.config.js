require('dotenv').config()
require("@nomiclabs/hardhat-waffle")

const accounts = [ process.env.PRIVATE_KEY ]

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
module.exports = {
  networks: {
    goerli: {
      url: `https://eth-goerli.alchemyapi.io/v2/${process.env.ALCHEMY_API_KEY}`,
      accounts: accounts
    },
    ropsten: {
      url: `https://eth-ropsten.alchemyapi.io/v2/${process.env.ALCHEMY_API_KEY}`,
      accounts: accounts
    },
  },
  solidity: "0.8.6",
};