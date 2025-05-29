account = {
  "type": "object",
  "properties": {
    "account_sid": {"type": "string", "print": True},
    "friendly_name": {"type": "string", "print": True},
    "status": {"type": "string", "print": True},
    "fraud_score": {"type": "integer", "print": True},
    "cntSubAccts": {"type": "integer", "print": True},
    "cntOwnMsgServices": {"type": "integer", "print": True},
    "cntAllMsgServices": {"type": "integer", "print": True},
    "cntOwnMsgSends": {"type": "integer", "print": True},
    "cntOwnOptOuts": {
      "type": "array",
      "print": True,
      "items": {
        "type": "object",
        "properties": {
          "optout_sid": {"type": "string", "print": True},
          "phone_number": {"type": "string", "print": True},
          "date_created": {"type": "string", "print": True}
        }
      }
    },
    "spendByProduct": {
      "type": "array",
      "print": False,
      "items": {
        "type": "object",
        "properties": {
          "product": {"type": "string", "print": True},
          "spend": {"type": "float", "print": True}
        }
      }
    },
    "spendByCountry": {
      "type": "array",
      "print": True,
      "items": {
        "type": "object",
        "properties": {
          "country": {"type": "string", "print": True},
          "spend": {"type": "float", "print": True}
        }
      }
    },
    "highSpendSubAccts": {
      "type": "array",
      "print": True,
      "items": {
        "type": "object",
        "properties": {
          "account_sid": {"type": "string", "print": True},
          "account_name": {"type": "string", "print": True},
          "spendByProduct": {
            "type": "array",
            "print": False,
            "items": {
              "type": "object",
              "properties": {
                "product": {"type": "string", "print": True},
                "spend": {"type": "float", "print": True}
              }
            }
          }
        }
      }
    },
    "allNumbers": {
      "type": "array",
      "print": True,
      "items": {
        "type": "object",
        "properties": {
          "phone_number": {"type": "string", "print": True},
          "type_name": {"type": "string", "print": True},
          "cnt": {"type": "integer", "print": True}
        }
      }
    },
    "ownNumbers": {
      "type": "array",
      "print": True,
      "items": {
        "type": "object",
        "properties": {
          "phone_number": {"type": "string", "print": True},
          "type_name": {"type": "string", "print": True},
          "cnt": {"type": "integer", "print": True}
        }
      }
    },
    "ownShortcodes": {
      "type": "array",
      "print": True,
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string", "print": True},
          "provider": {"type": "string", "print": True},
          "region": {"type": "string", "print": True}
        }
      }
    }
  }
}
