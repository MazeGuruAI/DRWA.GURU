#!/usr/bin/env python3
"""
Web3以太坊MCP服务器 - 完整版本
基于fastmcp、web3.py和requests，提供完整的以太坊区块链交互功能
包含链上数据查询、ERC20合约编译部署、代币转账等功能

功能模块:
1. 链上数据查询: ETH余额、Gas价格、区块信息、交易计数
2. ERC20合约: 动态编译、智能部署、代币转账、余额查询  
3. 网络支持: 主网、测试网、Layer2网络

使用方法:
pip install fastmcp web3 eth-utils python-dotenv py-solc-x requests
python tools/web3_mcp_server.py
"""

import os
import logging
import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

from fastmcp import FastMCP

# Web3相关导入
try:
    from web3 import Web3
    from eth_utils import is_address, to_checksum_address
    HAS_WEB3 = True
except ImportError:
    HAS_WEB3 = False
    print("Error: Please install web3: pip install web3 eth-utils")
    exit(1)

# Solidity编译器导入
try:
    from solcx import compile_source, install_solc, set_solc_version
    HAS_SOLCX = True
except ImportError:
    HAS_SOLCX = False
    print("Warning: py-solc-x not found. Using pre-compiled bytecode for ERC20 contracts.")

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量和配置文件读取配置
WALLET_PRIVATE_KEY = os.getenv('WALLET_PRIVATE_KEY')
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
INFURA_API_KEY = os.getenv('INFURA_API_KEY')

# 从配置文件加载Infura API Key（作为备选）
def load_infura_key_from_config():
    """从配置文件加载Infura API Key"""
    config_path = os.path.join(os.path.dirname(__file__), 'infurakey.conf')
    try:
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('INFURA_API_KEY'):
                    key = line.split('=')[1].strip()
                    return key
    except FileNotFoundError:
        logger.debug(f"Infura config file not found: {config_path}")
    except Exception as e:
        logger.debug(f"Error reading Infura config: {e}")
    return None

# 优先使用环境变量，然后尝试配置文件
if not INFURA_API_KEY:
    INFURA_API_KEY = load_infura_key_from_config()

if not INFURA_API_KEY:
    logger.warning("Infura API key not found, some features will use public endpoints")

# 网络配置生成函数
def get_networks():
    """根据Infura API Key动态生成网络配置"""
    networks = {}
    
    if INFURA_API_KEY:
        # 有Infura API Key时的完整网络配置
        networks.update({
            "mainnet": {
                "name": "Ethereum Mainnet",
                "rpc_url": f"https://mainnet.infura.io/v3/{INFURA_API_KEY}",
                "chain_id": 1,
                "explorer": "https://etherscan.io",
                "type": "mainnet"
            },
            "sepolia": {
                "name": "Sepolia Testnet",
                "rpc_url": f"https://sepolia.infura.io/v3/{INFURA_API_KEY}",
                "chain_id": 11155111,
                "explorer": "https://sepolia.etherscan.io",
                "type": "testnet"
            },
            "goerli": {
                "name": "Goerli Testnet", 
                "rpc_url": f"https://goerli.infura.io/v3/{INFURA_API_KEY}",
                "chain_id": 5,
                "explorer": "https://goerli.etherscan.io",
                "type": "testnet"
            },
            "polygon": {
                "name": "Polygon Mainnet",
                "rpc_url": f"https://polygon-mainnet.infura.io/v3/{INFURA_API_KEY}",
                "chain_id": 137,
                "explorer": "https://polygonscan.com",
                "type": "layer2"
            },
            "arbitrum": {
                "name": "Arbitrum One",
                "rpc_url": f"https://arbitrum-mainnet.infura.io/v3/{INFURA_API_KEY}",
                "chain_id": 42161,
                "explorer": "https://arbiscan.io",
                "type": "layer2"
            },
            "optimism": {
                "name": "Optimism Mainnet",
                "rpc_url": f"https://optimism-mainnet.infura.io/v3/{INFURA_API_KEY}",
                "chain_id": 10,
                "explorer": "https://optimistic.etherscan.io",
                "type": "layer2"
            }
        })
    else:
        # 无Infura API Key时使用公共端点
        networks.update({
            "mainnet": {
                "name": "Ethereum Mainnet",
                "rpc_url": "https://eth.llamarpc.com",
                "chain_id": 1,
                "explorer": "https://etherscan.io",
                "type": "mainnet"
            },
            "polygon": {
                "name": "Polygon Mainnet",
                "rpc_url": "https://polygon-rpc.com",
                "chain_id": 137,
                "explorer": "https://polygonscan.com",
                "type": "layer2"
            }
        })
    
    return networks

NETWORKS = get_networks()

# 区分可部署合约的测试网络
TESTNETWORKS = {k: v for k, v in NETWORKS.items() if v.get("type") == "testnet"}

# ERC20合约相关常量和ABI
ERC20_ABI = [
    {"inputs": [{"internalType": "string", "name": "_name", "type": "string"}, {"internalType": "string", "name": "_symbol", "type": "string"}, {"internalType": "uint256", "name": "_totalSupply", "type": "uint256"}], "stateMutability": "nonpayable", "type": "constructor"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}], "name": "Approval", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}], "name": "Transfer", "type": "event"},
    {"inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "address", "name": "", "type": "address"}], "name": "allowance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "decimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "name", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "totalSupply", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "from", "type": "address"}, {"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "name": "transferFrom", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"}
]

ERC20_SOURCE_CODE = '''
pragma solidity ^0.8.19;

contract SimpleERC20 {
    string public name;
    string public symbol;
    uint8 public decimals = 18;
    uint256 public totalSupply;
    
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    constructor(string memory _name, string memory _symbol, uint256 _totalSupply) {
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply * 10**decimals;
        balanceOf[msg.sender] = totalSupply;
        emit Transfer(address(0), msg.sender, totalSupply);
    }
    
    function transfer(address to, uint256 value) public returns (bool) {
        require(balanceOf[msg.sender] >= value, "Insufficient balance");
        require(to != address(0), "Cannot transfer to zero address");
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }
    
    function approve(address spender, uint256 value) public returns (bool) {
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }
    
    function transferFrom(address from, address to, uint256 value) public returns (bool) {
        require(balanceOf[from] >= value, "Insufficient balance");
        require(allowance[from][msg.sender] >= value, "Insufficient allowance");
        require(to != address(0), "Cannot transfer to zero address");
        balanceOf[from] -= value;
        balanceOf[to] += value;
        allowance[from][msg.sender] -= value;
        emit Transfer(from, to, value);
        return true;
    }
}
'''

# 预编译的ERC20字节码（简化版）
ERC20_BYTECODE = "0x608060405260126002600a6101000a81548160ff021916908360ff1602179055503480156200002d57600080fd5b506040516200188138038062001881833981016040528101906200005391906200032f565b82600090816200006491906200060a565b5081600190816200007691906200060a565b50600260009054906101000a900460ff16600a6200009591906200088156005081620000a29190620008d2565b600381905550600354600460003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055503373ffffffffffffffffffffffffffffffffffffffff16600073ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6003546040516200015091906200092e565b60405180910390a35050506200094b565b"

# 辅助函数
def get_web3_instance(network: str) -> Web3:
    """获取Web3实例"""
    if network not in NETWORKS:
        raise ValueError(f"不支持的网络: {network}")
    
    rpc_url = NETWORKS[network]["rpc_url"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        raise ConnectionError(f"无法连接到{network}网络")
    
    return w3

def compile_erc20_contract() -> Tuple[Optional[str], Optional[list]]:
    """编译ERC20合约，返回字节码和ABI"""
    if not HAS_SOLCX:
        logger.warning("没有安装py-solc-x，使用预编译的字节码")
        return None, None
    
    try:
        install_solc('0.8.19')
        set_solc_version('0.8.19')
        logger.info("正在编译ERC20合约...")
        compiled_sol = compile_source(ERC20_SOURCE_CODE)
        contract_interface = compiled_sol['<stdin>:SimpleERC20']
        bytecode = contract_interface['bin']
        abi = contract_interface['abi']
        logger.info(f"✅ 合约编译成功，字节码长度: {len(bytecode)} 字符")
        return '0x' + bytecode, abi
    except Exception as e:
        logger.error(f"合约编译失败: {e}")
        return None, None

# 创建FastMCP实例
mcp = FastMCP("web3-ethereum-tools")

# ==================== 链上数据查询工具 ====================

@mcp.tool()
def get_eth_balance(address: str, network: str = "mainnet") -> str:
    """查询以太坊地址的ETH余额
    
    Args:
        address: 以太坊地址（0x开头的42位十六进制字符串）
        network: 网络名称，支持：mainnet, sepolia, goerli, polygon, arbitrum, optimism
    """
    try:
        if not is_address(address):
            return "❌ 无效的以太坊地址格式"
            
        if network not in NETWORKS:
            return f"❌ 不支持的网络: {network}。支持的网络: {', '.join(NETWORKS.keys())}"
            
        address = to_checksum_address(address)
        rpc_url = NETWORKS[network]["rpc_url"]
        
        # 同步调用（使用requests而不是async）
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [address, "latest"],
            "id": 1
        }
        
        response = requests.post(rpc_url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            return f"❌ RPC错误: {data['error']['message']}"
            
        balance_wei = data.get("result")
        balance_eth = int(balance_wei, 16) / 10**18
        
        result = f"""# ETH余额查询结果

**地址**: `{address}`
**网络**: {NETWORKS[network]['name']}
**余额**: {round(balance_eth, 6)} ETH ({balance_wei} wei)
**查询时间**: {datetime.now().isoformat()}

[在区块浏览器中查看]({NETWORKS[network]['explorer']}/address/{address})
"""
        return result
            
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"

@mcp.tool()
def get_gas_price(network: str = "mainnet") -> str:
    """查询当前网络的Gas价格
    
    Args:
        network: 网络名称，支持：mainnet, sepolia, goerli, polygon, arbitrum, optimism
    """
    try:
        if network not in NETWORKS:
            return f"❌ 不支持的网络: {network}。支持的网络: {', '.join(NETWORKS.keys())}"
            
        rpc_url = NETWORKS[network]["rpc_url"]
        
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_gasPrice",
            "params": [],
            "id": 1
        }
        
        response = requests.post(rpc_url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            return f"❌ RPC错误: {data['error']['message']}"
            
        gas_price_wei = data.get("result")
        gas_price_gwei = int(gas_price_wei, 16) / 10**9
        
        result = f"""# Gas价格查询结果

**网络**: {NETWORKS[network]['name']}
**Gas价格**: {round(gas_price_gwei, 2)} Gwei ({gas_price_wei} wei)
**查询时间**: {datetime.now().isoformat()}
"""
        return result
            
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"

@mcp.tool()
def get_block_number(network: str = "mainnet") -> str:
    """查询最新区块号
    
    Args:
        network: 网络名称，支持：mainnet, sepolia, goerli, polygon, arbitrum, optimism
    """
    try:
        if network not in NETWORKS:
            return f"❌ 不支持的网络: {network}。支持的网络: {', '.join(NETWORKS.keys())}"
            
        rpc_url = NETWORKS[network]["rpc_url"]
        
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }
        
        response = requests.post(rpc_url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            return f"❌ RPC错误: {data['error']['message']}"
            
        block_number_hex = data.get("result")
        block_number = int(block_number_hex, 16)
        
        result = f"""# 最新区块查询结果

**网络**: {NETWORKS[network]['name']}
**区块号**: {block_number:,} (0x{block_number:x})
**查询时间**: {datetime.now().isoformat()}

[在区块浏览器中查看]({NETWORKS[network]['explorer']}/block/{block_number})
"""
        return result
            
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"

@mcp.tool()
def get_network_info() -> str:
    """获取支持的网络信息和状态"""
    try:
        infura_status = "✅ 已配置" if INFURA_API_KEY else "❌ 未配置"
        wallet_status = "✅ 已配置" if WALLET_PRIVATE_KEY else "❌ 未配置"
        
        network_info = []
        for net_id, net_config in NETWORKS.items():
            network_info.append(f"- **{net_config['name']}** ({net_id})")
            network_info.append(f"  - 类型: {net_config.get('type', 'unknown')}")
            network_info.append(f"  - RPC: `{net_config['rpc_url'][:50]}...`")
            network_info.append(f"  - 浏览器: {net_config['explorer']}")
            
        result = f"""# 网络信息查询结果

**Infura API Key 状态**: {infura_status}
**钱包私钥状态**: {wallet_status}
**支持的网络**: {len(NETWORKS)} 个
**可部署合约的测试网**: {len(TESTNETWORKS)} 个

## 网络列表

{''.join([line + '\n' for line in network_info])}
**查询时间**: {datetime.now().isoformat()}
"""
        return result
        
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"

# ==================== ERC20合约部署和管理工具 ====================

@mcp.tool()
def deploy_erc20_contract(name: str, symbol: str, total_supply: int, network: str = "sepolia") -> str:
    """在测试网络上部署新的ERC20合约（集成完整编译和部署流程）
    
    Args:
        name: 代币名称 (例如: "My Token")
        symbol: 代币符号 (例如: "MTK")
        total_supply: 代币总供应量 (例如: 1000000)
        network: 网络名称，支持: sepolia, goerli
    """
    try:
        if not WALLET_PRIVATE_KEY:
            return "❌ 缺少WALLET_PRIVATE_KEY环境变量，请在.env文件中设置"
        
        if network not in TESTNETWORKS:
            return f"❌ 不支持的测试网络: {network}。支持的测试网络: {', '.join(TESTNETWORKS.keys())}"
        
        logger.info(f"开始部署ERC20合约: {name} ({symbol})，总供应量: {total_supply}")
        
        # 第一步：尝试动态编译合约
        logger.info("步骤1/4: 尝试动态编译ERC20合约...")
        compiled_bytecode, compiled_abi = compile_erc20_contract()
        
        # 选择使用哪个字节码和ABI
        if compiled_bytecode and compiled_abi:
            logger.info("✅ 使用动态编译的合约字节码")
            use_bytecode = compiled_bytecode
            use_abi = compiled_abi
            compilation_method = "动态编译"
        else:
            logger.info("⚠️ 动态编译失败，使用预编译的字节码")
            use_bytecode = ERC20_BYTECODE
            use_abi = ERC20_ABI
            compilation_method = "预编译字节码"
        
        # 第二步：连接Web3
        logger.info("步骤2/4: 连接到区块链网络...")
        w3 = get_web3_instance(network)
        
        # 准备账户
        if WALLET_PRIVATE_KEY.startswith('0x'):
            private_key = WALLET_PRIVATE_KEY
        else:
            private_key = '0x' + WALLET_PRIVATE_KEY
        
        account = w3.eth.account.from_key(private_key)
        logger.info(f"使用部署账户: {account.address}")
        
        # 检查余额
        balance = w3.eth.get_balance(account.address)
        balance_eth = w3.from_wei(balance, 'ether')
        logger.info(f"账户余额: {balance_eth:.6f} ETH")
        
        if balance_eth < 0.01:  # 需要至少0.01 ETH来部署合约
            return f"❌ 账户余额不足。当前余额: {balance_eth:.6f} ETH，建议至少0.01 ETH"
        
        # 第三步：准备部署交易
        logger.info("步骤3/4: 准备部署交易...")
        
        # 创建合约实例
        contract = w3.eth.contract(abi=use_abi, bytecode=use_bytecode)
        
        # 构建构造函数参数
        constructor_args = (name, symbol, total_supply)
        logger.info(f"合约构造参数: 名称={name}, 符号={symbol}, 总供应量={total_supply}")
        
        # 估算gas费用
        try:
            estimated_gas = contract.constructor(*constructor_args).estimate_gas({
                'from': account.address
            })
            gas_limit = int(estimated_gas * 1.2)
            logger.info(f"预估Gas: {estimated_gas:,}，设置Gas限制: {gas_limit:,}")
        except Exception as gas_error:
            logger.warning(f"Gas估算失败: {gas_error}，使用默认值")
            gas_limit = 3000000
        
        # 构建交易
        gas_price = max(w3.to_wei('2', 'gwei'), w3.eth.gas_price * 2)
        transaction = contract.constructor(*constructor_args).build_transaction({
            'chainId': TESTNETWORKS[network]["chain_id"],
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'from': account.address
        })
        
        # 第四步：签名、发送并等待确认
        logger.info("步骤4/4: 发送交易并等待确认...")
        
        # 签名并发送交易
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        logger.info(f"交易已发送: {tx_hash.hex()}")
        
        # 等待交易确认
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if tx_receipt.status == 1:
            contract_address = tx_receipt.contractAddress
            logger.info(f"✅ 合约部署成功！地址: {contract_address}")
            
            # 计算实际费用
            actual_fee = tx_receipt.gasUsed * gas_price
            actual_fee_eth = w3.from_wei(actual_fee, 'ether')
            
            result = f"""# ERC20合约部署成功 ✅

**合约地址**: `{contract_address}`
**代币名称**: {name}
**代币符号**: {symbol}
**总供应量**: {total_supply:,} 代币
**编译方式**: {compilation_method}
**网络**: {TESTNETWORKS[network]['name']}
**部署者**: `{account.address}`
**交易哈希**: `{tx_hash.hex()}`
**Gas 使用**: {tx_receipt.gasUsed:,} / {gas_limit:,}
**部署费用**: {actual_fee_eth:.6f} ETH
**部署时间**: {datetime.now().isoformat()}

[在区块浏览器中查看合约]({TESTNETWORKS[network]['explorer']}/address/{contract_address})
[在区块浏览器中查看交易]({TESTNETWORKS[network]['explorer']}/tx/{tx_hash.hex()})

**注意**: 请保存合约地址以便后续使用！
"""
            return result
        else:
            logger.error(f"合约部署失败，交易状态: {tx_receipt.status}")
            return f"❌ 合约部署失败，交易状态: {tx_receipt.status}"
            
    except Exception as e:
        logger.error(f"部署过程中发生错误: {str(e)}")
        return f"❌ 部署失败: {str(e)}"

@mcp.tool()
def check_erc20_balance(contract_address: str, wallet_address: str, network: str = "sepolia") -> str:
    """查询ERC20代币余额
    
    Args:
        contract_address: ERC20合约地址
        wallet_address: 钱包地址
        network: 网络名称，支持: mainnet, sepolia, goerli, polygon, arbitrum, optimism
    """
    try:
        if not is_address(contract_address):
            return "❌ 无效的合约地址格式"
            
        if not is_address(wallet_address):
            return "❌ 无效的钱包地址格式"
        
        if network not in NETWORKS:
            return f"❌ 不支持的网络: {network}。支持的网络: {', '.join(NETWORKS.keys())}"
        
        # 连接Web3
        w3 = get_web3_instance(network)
        
        # 创建合约实例
        contract = w3.eth.contract(
            address=to_checksum_address(contract_address),
            abi=ERC20_ABI
        )
        
        # 查询余额和代币信息
        balance = contract.functions.balanceOf(to_checksum_address(wallet_address)).call()
        
        try:
            token_name = contract.functions.name().call()
            token_symbol = contract.functions.symbol().call()
            total_supply = contract.functions.totalSupply().call()
            decimals = contract.functions.decimals().call()
        except:
            token_name = "Unknown Token"
            token_symbol = "UNK"
            total_supply = 0
            decimals = 18
        
        # 转换为可读格式
        balance_readable = balance / (10 ** decimals)
        total_supply_readable = total_supply / (10 ** decimals)
        
        result = f"""# ERC20代币余额查询结果

**合约地址**: `{contract_address}`
**代币信息**: {token_name} ({token_symbol})
**精度**: {decimals} 位
**钱包地址**: `{wallet_address}`
**代币余额**: {balance_readable:,.6f} {token_symbol}
**原始余额**: {balance:,} 最小单位
**总供应量**: {total_supply_readable:,.6f} {token_symbol}
**网络**: {NETWORKS[network]['name']}
**查询时间**: {datetime.now().isoformat()}

[在区块浏览器中查看合约]({NETWORKS[network]['explorer']}/address/{contract_address})
[在区块浏览器中查看钱包]({NETWORKS[network]['explorer']}/address/{wallet_address})
"""
        return result
            
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"

@mcp.tool()
def transfer_erc20_tokens(contract_address: str, to_address: str, amount: float, network: str = "sepolia") -> str:
    """使用ERC20合约转账代币
    
    Args:
        contract_address: ERC20合约地址
        to_address: 接收者地址
        amount: 转账数量 (代币单位，会自动转换为最小单位)
        network: 网络名称，支持: sepolia, goerli, mainnet, polygon, arbitrum, optimism
    """
    try:
        if not WALLET_PRIVATE_KEY:
            return "❌ 缺少WALLET_PRIVATE_KEY环境变量，请在.env文件中设置"
        
        if not is_address(contract_address):
            return "❌ 无效的合约地址格式"
            
        if not is_address(to_address):
            return "❌ 无效的接收者地址格式"
        
        if network not in NETWORKS:
            return f"❌ 不支持的网络: {network}。支持的网络: {', '.join(NETWORKS.keys())}"
        
        # 连接Web3
        w3 = get_web3_instance(network)
        
        # 准备账户
        if WALLET_PRIVATE_KEY.startswith('0x'):
            private_key = WALLET_PRIVATE_KEY
        else:
            private_key = '0x' + WALLET_PRIVATE_KEY
            
        account = w3.eth.account.from_key(private_key)
        
        # 创建合约实例
        contract = w3.eth.contract(
            address=to_checksum_address(contract_address),
            abi=ERC20_ABI
        )
        
        # 获取代币信息
        try:
            decimals = contract.functions.decimals().call()
            token_name = contract.functions.name().call()
            token_symbol = contract.functions.symbol().call()
        except:
            decimals = 18
            token_name = "Unknown Token"
            token_symbol = "UNK"
        
        # 转换为最小单位
        amount_wei = int(amount * (10 ** decimals))
        
        # 检查代币余额
        token_balance = contract.functions.balanceOf(account.address).call()
        if token_balance < amount_wei:
            token_balance_readable = token_balance / (10 ** decimals)
            return f"❌ 代币余额不足。当前余额: {token_balance_readable:.6f} {token_symbol}，尝试转账: {amount} {token_symbol}"
        
        # 检查ETH余额（用于支付gas费）
        eth_balance = w3.eth.get_balance(account.address)
        if eth_balance < w3.to_wei('0.001', 'ether'):
            return f"❌ ETH余额不足支付gas费。当前余额: {w3.from_wei(eth_balance, 'ether'):.6f} ETH"
        
        # 构建转账交易
        transaction = contract.functions.transfer(
            to_checksum_address(to_address), 
            amount_wei
        ).build_transaction({
            'chainId': NETWORKS[network]["chain_id"],
            'gas': 100000,
            'gasPrice': max(w3.to_wei('2', 'gwei'), w3.eth.gas_price),
            'nonce': w3.eth.get_transaction_count(account.address),
            'from': account.address
        })
        
        # 签名并发送交易
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        # 等待交易确认
        logger.info(f"等待转账交易确认: {tx_hash.hex()}")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if tx_receipt.status == 1:
            result = f"""# ERC20代币转账成功 ✅

**合约地址**: `{contract_address}`
**代币信息**: {token_name} ({token_symbol})
**发送者**: `{account.address}`
**接收者**: `{to_address}`
**转账数量**: {amount} {token_symbol} ({amount_wei:,} 最小单位)
**网络**: {NETWORKS[network]['name']}
**交易哈希**: `{tx_hash.hex()}`
**Gas 使用**: {tx_receipt.gasUsed:,}
**转账时间**: {datetime.now().isoformat()}

[在区块浏览器中查看交易]({NETWORKS[network]['explorer']}/tx/{tx_hash.hex()})
"""
            return result
        else:
            return f"❌ 转账失败，交易状态: {tx_receipt.status}"
            
    except Exception as e:
        return f"❌ 转账失败: {str(e)}"

# 启动服务器时显示配置信息
if __name__ == "__main__":
    if INFURA_API_KEY:
        logger.info(f"Starting Web3 MCP Server with Infura API (Key: {INFURA_API_KEY[:8]}...)")
        logger.info(f"Supported networks: {', '.join(NETWORKS.keys())}")
    else:
        logger.warning("Starting Web3 MCP Server with public endpoints")
    
    if WALLET_PRIVATE_KEY:
        account_address = Web3().eth.account.from_key('0x' + WALLET_PRIVATE_KEY if not WALLET_PRIVATE_KEY.startswith('0x') else WALLET_PRIVATE_KEY).address
        logger.info(f"Wallet Address: {account_address}")
        logger.info(f"Testnet deployment networks: {', '.join(TESTNETWORKS.keys())}")
    else:
        logger.warning("No wallet private key configured. Contract deployment disabled.")
    
    # 配置使用streamable-http模式
    mcp.run(transport="stdio")