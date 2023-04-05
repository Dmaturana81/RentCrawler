db.getCollection("houses").find(
    {
        "kind": "Sale"
    }, 
    {
        "address.bairro": 1.0,
        "prices.sell": 1.0,
        "details.type": 1.0,
        "details.size": 1.0
    }
)
