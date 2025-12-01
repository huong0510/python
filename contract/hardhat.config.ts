import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

import * as dotenv from "dotenv";
dotenv.config();

const INFURA_API_KEY = process.env.INFURA_API_KEY || "";
const SEPOLIA_PRIVATE_KEY = process.env.SEPOLIA_PRIVATE_KEY || "";

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.28",
    settings: {
      optimizer: {
        enabled: true,   // Bật optimizer
        runs: 200        // Số lần tối ưu (200 là mặc định phổ biến)
      },
      viaIR: true        // Bật viaIR để giảm lỗi stack too deep
    }
  },
  etherscan: {
    apiKey: "TI5SA79CG77FB4T6KPCZ3QZFVU2NIUNPMC",  // API key Etherscan
  },
  networks: {
    sepolia: {
      url: `https://sepolia.infura.io/v3/${INFURA_API_KEY}`,
      accounts: [SEPOLIA_PRIVATE_KEY],
    },
  },
};

export default config;
