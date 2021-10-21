pragma solidity ^0.4.11;

contract ankitcoin_ico {
    
    uint public max_ankitcoins = 500000;
    uint public usd_to_ankitcoins = 5000;
    
    uint public total_ankitcoins_bought = 0;
    
    // mapping from investor address to their equity
    mapping(address => uint) equity_ankitcoins;
    mapping(address => uint) equity_usd;
    
    // amount_invested - number investor wants to buy
    modifier can_buy_ankitcoins(uint amount_invested) {
        require (amount_invested * usd_to_ankitcoins + total_ankitcoins_bought < max_ankitcoins);
        _;
    }
    
    // get equity in ankitcoins
    function equity_in_ankitcoin(address investor) external constant returns (uint) {
        return equity_ankitcoins[address];
    }
    function equity_in_usd(address investor) external constant returns (uint) {
        return equity_usd[address];
    }
    
    // allow people to buy coins 
    function buy_coins(address investor, uint usd_invested) external
    can_buy_ankitcoins(usd_invested) {
        equity_ankitcoins[investor] += usd_invested*usd_to_ankitcoins;
        equity_usd[investor] = equity_ankitcoins[investor] / usd_to_ankitcoins;
        total_ankitcoins_bought += equity_ankitcoins[investor]
    }
    
    // allow selling coins
    function sell_coins(address investor, uint ankitcoins_to_sell) external {
        equity_ankitcoins[investor] -= ankitcoins_to_sell;
        equity_usd[investor] = equity_ankitcoins[investor] / usd_to_ankitcoins;
        total_ankitcoins_bought -= equity_ankitcoins[investor];
    }
}
