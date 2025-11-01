# Bloomberg B-PIPE API Illustration

This project demonstrates how to use Bloomberg's **B-PIPE** (Bloomberg Pipe) API to access financial market data. B-PIPE is Bloomberg's enterprise data distribution platform that provides real-time and reference data to applications.

## Overview

B-PIPE allows applications to:
- **Authenticate** using application or user credentials
- **Request reference data** (static security information like company names, fundamentals)
- **Subscribe to market data** (real-time price updates, volume, bids/asks)
- **Handle events** asynchronously as market data changes occur

## Prerequisites

**Note:** This is an illustration that shows the expected behavior. Running this code requires:
- Access to Bloomberg B-PIPE infrastructure
- The `blpapi` Python package (`pip install blpapi`)
- Valid Bloomberg credentials and data entitlements

## Running the Example

```bash
uv run python python/bloomberg-bpipe/main.py
```

## Key Concepts

### 1. Authentication Modes

B-PIPE supports two authentication approaches:

| Mode | Use Case | Advantages | Disadvantages |
|------|----------|------------|---------------|
| **Application Auth** | Server applications, analytics engines | Simpler setup, single auth | Cannot track individual users |
| **User Auth** | Desktop apps, compliance requirements | Per-user entitlements, audit trail | More complex, additional latency |

### 2. Services

- `//blp/refdata` - Reference Data Service (static information)
- `//blp/mktdata` - Market Data Service (real-time prices)
- `//blp/instruments` - Instrument lookup and search

## Code Structure and Expected Output

### Part 1: Initialization and Configuration (Lines 54-59)

**Source Code:**
```python
54    # Line 54: Session options configuration
55    print(f"\n{'='*80}")
56    print("STEP 1: CONFIGURING SESSION OPTIONS")
57    print(f"{'='*80}")
58    print(f"[Line 54-59] Setting up connection parameters:")
59    print(f"  • Host: {self.host}")
```

**Expected Output:**
```
================================================================================
STEP 1: CONFIGURING SESSION OPTIONS
================================================================================
[Line 54-59] Setting up connection parameters:
  • Host: bpipe-gateway.bloomberg.com
  • Port: 8194
  • Application Name: MyTradingApp
  • User Authentication Required: False
```

**Annotation:** The session configuration establishes how the client will connect to Bloomberg's servers. For B-PIPE, you typically connect to a dedicated gateway server (not localhost). Port 8194 is the standard B-PIPE port.

---

### Part 2: Application Authentication (Lines 66-85)

**Source Code:**
```python
66    def authenticate_application(self) -> bool:
67        """
68        Line 66-85: Application authentication.
69
70        Application authentication allows the entire application to access Bloomberg data.
71        This is typically used for server-based applications where the app itself is trusted.
72        """
73        print(f"\n{'='*80}")
74        print("STEP 2: APPLICATION AUTHENTICATION")
75        print(f"{'='*80}")
76
77        if not self.app_name:
78            print("[Line 77] No application name provided - skipping app authentication")
79            return True
80
81        print(f"[Line 80] Authenticating application: {self.app_name}")
82        print("[Line 81] Sending authentication token request...")
83        print("[Line 82] Waiting for authentication response...")
84
85        print(f"[Line 85] ✓ Application '{self.app_name}' authenticated successfully")
```

**Expected Output:**
```
================================================================================
STEP 2: APPLICATION AUTHENTICATION
================================================================================
[Line 80] Authenticating application: MyTradingApp
[Line 81] Sending authentication token request...
[Line 82] Waiting for authentication response...
[Line 85] ✓ Application 'MyTradingApp' authenticated successfully
```

**Annotation:** Application authentication validates that your application is registered with Bloomberg and has permission to access data. Bloomberg must pre-register your application name before it can be used. This authentication applies to all users of the application.

---

### Part 3: User Authentication (Lines 88-110)

**Source Code:**
```python
88    def authenticate_user(self, user_id: str, ip_address: str) -> bool:
89        """
90        Line 88-110: User authentication.
91
92        User authentication is more restrictive and ties data access to specific users.
93        This is required when you need to track individual user access or when
94        Bloomberg licensing requires per-user authentication.
95
96        Args:
97            user_id: Bloomberg UUID or user identifier
98            ip_address: IP address of the user's workstation
99        """
...
107       print(f"[Line 107] Authenticating user: {user_id}")
108       print(f"[Line 108] User IP address: {ip_address}")
109       print("[Line 109] Sending user authentication request...")
110       print(f"[Line 110] ✓ User '{user_id}' authenticated successfully")
```

**Expected Output (Scenario 2 only):**
```
================================================================================
STEP 3: USER AUTHENTICATION
================================================================================
[Line 107] Authenticating user: john.doe@example.com
[Line 108] User IP address: 192.168.1.100
[Line 109] Sending user authentication request...
[Line 110] ✓ User 'john.doe@example.com' authenticated successfully
```

**Annotation:** User authentication validates individual users and enforces per-user data entitlements. The user's Bloomberg permissions determine what data they can access. This is required for compliance in many regulated environments.

---

### Part 4: Opening Services (Lines 113-135)

**Source Code:**
```python
113   def open_services(self):
114       """
115       Line 113-135: Opening Bloomberg services.
116
117       B-PIPE provides different services for different data types:
118       - //blp/refdata: Reference data (static security information)
119       - //blp/mktdata: Market data (real-time prices and updates)
120       - //blp/instruments: Instrument lookup and search
121       """
122       print(f"\n{'='*80}")
123       print("STEP 4: OPENING BLOOMBERG SERVICES")
124       print(f"{'='*80}")
125
126       services = [
127           "//blp/refdata",  # Reference Data Service
128           "//blp/mktdata",  # Market Data Service
129       ]
130
131       for service in services:
132           print(f"[Line 130] Opening service: {service}")
133           print(f"[Line 132] ✓ Service '{service}' opened successfully")
135       print("[Line 135] All required services are now available")
```

**Expected Output:**
```
================================================================================
STEP 4: OPENING BLOOMBERG SERVICES
================================================================================
[Line 130] Opening service: //blp/refdata
[Line 132] ✓ Service '//blp/refdata' opened successfully
[Line 130] Opening service: //blp/mktdata
[Line 132] ✓ Service '//blp/mktdata' opened successfully
[Line 135] All required services are now available
```

**Annotation:** Services must be opened before they can be used. Each service provides access to different types of data. The refdata service provides static information, while mktdata provides real-time streaming updates.

---

### Part 5: Reference Data Request (Lines 138-195)

**Source Code:**
```python
138   def request_reference_data(self, securities: list[str], fields: list[str]):
139       """
140       Line 138-195: Request reference data.
141
142       Reference data contains static or slowly-changing information about securities:
143       - Company fundamentals
144       - Security descriptions
145       - Credit ratings
146       - Corporate actions
...
157       print(f"[Line 157] Creating reference data request")
158       print(f"[Line 158] Securities: {securities}")
159       print(f"[Line 159] Fields: {fields}")
...
169       print(f"[Line 169] Sending request to //blp/refdata service...")
170       print(f"[Line 170] Waiting for response...\n")
```

**Expected Output:**
```
================================================================================
STEP 5: REQUESTING REFERENCE DATA
================================================================================
[Line 157] Creating reference data request
[Line 158] Securities: ['IBM US Equity', 'AAPL US Equity']
[Line 159] Fields: ['PX_LAST', 'NAME', 'COUNTRY', 'INDUSTRY_SECTOR', 'LAST_UPDATE']
[Line 169] Sending request to //blp/refdata service...
[Line 170] Waiting for response...

================================================================================
REFERENCE DATA RESPONSE
================================================================================

[Line 178] Security: IBM US Equity
[Line 179] ────────────────────────────────────────────────────────
[Line 181]   PX_LAST        = 147.52
[Line 182]   NAME           = INTERNATIONAL BUSINESS MACHINES CORP
[Line 183]   COUNTRY        = US
[Line 184]   INDUSTRY_SECTOR = Technology
[Line 185]   LAST_UPDATE    = 2024-10-31 16:00:00

[Line 178] Security: AAPL US Equity
[Line 179] ────────────────────────────────────────────────────────
[Line 187]   PX_LAST        = 225.91
[Line 188]   NAME           = APPLE INC
[Line 189]   COUNTRY        = US
[Line 190]   INDUSTRY_SECTOR = Technology
[Line 191]   LAST_UPDATE    = 2024-10-31 16:00:00

[Line 195] ✓ Reference data request completed
```

**Annotation:** Reference data requests are **synchronous** request/response operations. You specify the securities and fields you want, send the request, and receive a single response containing all the requested data. This is ideal for static information that doesn't change frequently.

**Key Fields Explained:**
- `PX_LAST`: Last traded price
- `NAME`: Full legal name of the security
- `COUNTRY`: Country of incorporation
- `INDUSTRY_SECTOR`: Industry classification
- `LAST_UPDATE`: Timestamp of the last data update

---

### Part 6: Market Data Subscription (Lines 198-280)

**Source Code:**
```python
198   def subscribe_market_data(self, securities: list[str], fields: list[str]):
199       """
200       Line 198-280: Subscribe to real-time market data.
201
202       Market data subscriptions provide continuous updates for:
203       - Real-time prices (BID, ASK, LAST)
204       - Trading volume
205       - Market depth
206       - Trade ticks
207
208       Once subscribed, updates are pushed to the client as they occur.
...
217       print(f"[Line 217] Creating market data subscription")
218       print(f"[Line 218] Securities: {securities}")
219       print(f"[Line 219] Fields: {fields}")
...
227       print(f"[Line 227] Subscription request sent to //blp/mktdata service")
228       print(f"[Line 228] Subscription active - will receive updates as they occur\n")
```

**Expected Output:**
```
================================================================================
STEP 6: SUBSCRIBING TO REAL-TIME MARKET DATA
================================================================================
[Line 217] Creating market data subscription
[Line 218] Securities: ['IBM US Equity', 'AAPL US Equity']
[Line 219] Fields: ['BID', 'ASK', 'LAST_PRICE', 'VOLUME']
[Line 227] Subscription request sent to //blp/mktdata service
[Line 228] Subscription active - will receive updates as they occur

================================================================================
REAL-TIME MARKET DATA UPDATES
================================================================================

[Line 236] ─── SUBSCRIPTION SNAPSHOT (Initial Data) ───
[Line 237] Timestamp: 2024-10-31 14:23:45.123

[Line 240] IBM US Equity:
[Line 241]   BID        = 147.48
[Line 242]   ASK        = 147.52
[Line 243]   LAST_PRICE = 147.50
[Line 244]   VOLUME     = 3,245,678

[Line 240] AAPL US Equity:
[Line 246]   BID        = 225.88
[Line 247]   ASK        = 225.92
[Line 248]   LAST_PRICE = 225.90
[Line 249]   VOLUME     = 45,678,901

[Line 265] ─── UPDATE #1 ───
[Line 266] Timestamp: 2024-10-31 14:23:46.623
[Line 267] Security: IBM US Equity
[Line 268] Changes:
[Line 269]   LAST_PRICE   = 147.53
[Line 269]   VOLUME       = 3,246,100

[Line 270] ─── UPDATE #2 ───
[Line 271] Timestamp: 2024-10-31 14:23:47.423
[Line 272] Security: AAPL US Equity
[Line 273] Changes:
[Line 274]   BID          = 225.89
[Line 274]   ASK          = 225.93
[Line 274]   LAST_PRICE   = 225.91

[Line 275] ─── UPDATE #3 ───
[Line 276] Timestamp: 2024-10-31 14:23:48.523
[Line 277] Security: IBM US Equity
[Line 278] Changes:
[Line 279]   BID          = 147.50
[Line 279]   ASK          = 147.54
[Line 279]   LAST_PRICE   = 147.52

[Line 280] ✓ Market data subscription active (press Ctrl+C to stop)
```

**Annotation:** Market data subscriptions are **asynchronous push-based updates**. After subscribing:

1. **Initial Snapshot (Lines 236-249):** Bloomberg immediately sends current values for all subscribed fields
2. **Incremental Updates (Lines 265-279):** As market data changes, Bloomberg pushes only the changed fields to minimize bandwidth

This is more efficient than polling for real-time data and ensures you receive updates as quickly as possible.

**Key Fields Explained:**
- `BID`: Highest price a buyer is willing to pay
- `ASK`: Lowest price a seller is willing to accept
- `LAST_PRICE`: Price of the most recent trade
- `VOLUME`: Total number of shares traded today

**Bid-Ask Spread:** The difference between ASK and BID (e.g., 147.52 - 147.48 = $0.04) represents the market maker's profit margin and market liquidity.

---

### Part 7: Session Cleanup (Lines 283-293)

**Source Code:**
```python
283   def close_session(self):
284       """
285       Line 283-293: Clean up and close the session.
286
287       Proper cleanup ensures:
288       - All subscriptions are cancelled
289       - Network connections are closed
290       - Resources are freed
291       """
292       print("[Line 292] Closing Bloomberg session...")
293       print("[Line 293] ✓ Session closed successfully")
```

**Expected Output:**
```
================================================================================
STEP 7: CLOSING SESSION
================================================================================
[Line 292] Closing Bloomberg session...
[Line 293] ✓ Session closed successfully
```

**Annotation:** Always close sessions properly to:
- Cancel all active subscriptions (stops data flow)
- Release network connections
- Free memory and system resources
- Ensure clean disconnection from Bloomberg servers

---

## Complete Program Output

### Scenario 1: Application Authentication Mode

```
================================================================================
 BLOOMBERG B-PIPE API ILLUSTRATION
================================================================================

████████████████████████████████████████████████████████████████████████████████
█ SCENARIO 1: APPLICATION AUTHENTICATION MODE
████████████████████████████████████████████████████████████████████████████████

[Line 316-320] In this mode:
  • The application authenticates with Bloomberg using its app name
  • All users of the application share the same data entitlements
  • Typically used for server-based applications (web servers, analytics engines)
  • Requires Bloomberg to register your application name

================================================================================
STEP 1: CONFIGURING SESSION OPTIONS
================================================================================
[Line 54-59] Setting up connection parameters:
  • Host: bpipe-gateway.bloomberg.com
  • Port: 8194
  • Application Name: MyTradingApp
  • User Authentication Required: False

================================================================================
STEP 2: APPLICATION AUTHENTICATION
================================================================================
[Line 80] Authenticating application: MyTradingApp
[Line 81] Sending authentication token request...
[Line 82] Waiting for authentication response...
[Line 85] ✓ Application 'MyTradingApp' authenticated successfully

================================================================================
STEP 4: OPENING BLOOMBERG SERVICES
================================================================================
[Line 130] Opening service: //blp/refdata
[Line 132] ✓ Service '//blp/refdata' opened successfully
[Line 130] Opening service: //blp/mktdata
[Line 132] ✓ Service '//blp/mktdata' opened successfully
[Line 135] All required services are now available

[... Reference Data and Market Data sections as shown above ...]

================================================================================
STEP 7: CLOSING SESSION
================================================================================
[Line 292] Closing Bloomberg session...
[Line 293] ✓ Session closed successfully
```

### Scenario 2: User Authentication Mode

```
████████████████████████████████████████████████████████████████████████████████
█ SCENARIO 2: USER AUTHENTICATION MODE
████████████████████████████████████████████████████████████████████████████████

[Line 362-367] In this mode:
  • Individual users authenticate with their Bloomberg credentials
  • Each user has their own data entitlements based on their Bloomberg subscription
  • Typically required for:
    - Desktop applications where multiple users log in
    - Compliance requirements tracking individual user access
    - Bloomberg licensing that requires per-user authentication

================================================================================
STEP 1: CONFIGURING SESSION OPTIONS
================================================================================
[Line 54-59] Setting up connection parameters:
  • Host: bpipe-gateway.bloomberg.com
  • Port: 8194
  • Application Name: MyTradingApp
  • User Authentication Required: True

================================================================================
STEP 2: APPLICATION AUTHENTICATION
================================================================================
[Line 80] Authenticating application: MyTradingApp
[Line 81] Sending authentication token request...
[Line 82] Waiting for authentication response...
[Line 85] ✓ Application 'MyTradingApp' authenticated successfully

================================================================================
STEP 3: USER AUTHENTICATION
================================================================================
[Line 107] Authenticating user: john.doe@example.com
[Line 108] User IP address: 192.168.1.100
[Line 109] Sending user authentication request...
[Line 110] ✓ User 'john.doe@example.com' authenticated successfully

[... Services, Reference Data, and Market Data sections follow ...]
```

---

## Key Takeaways

### 1. Request vs Subscription Models

| Feature | Reference Data | Market Data |
|---------|----------------|-------------|
| **Pattern** | Request/Response | Publish/Subscribe |
| **Frequency** | On-demand | Continuous |
| **Data Type** | Static/slow-changing | Real-time updates |
| **Use Case** | Company info, fundamentals | Live prices, volume |
| **Bandwidth** | Low (one-time) | Higher (continuous stream) |

### 2. Authentication Best Practices

**Use Application Auth When:**
- Building server-side applications (web servers, APIs)
- All users should have the same data access
- You want simpler setup and maintenance

**Use User Auth When:**
- Building desktop applications with multiple users
- Need to enforce per-user data entitlements
- Compliance requires tracking individual access
- Bloomberg licensing requires per-user authentication

### 3. Security Identifiers

Bloomberg uses specific formats for security identifiers:
- `IBM US Equity` - US equity ticker
- `AAPL US Equity` - US equity ticker
- `/cusip/459200101` - CUSIP identifier
- `/isin/US4592001014` - ISIN identifier
- `T 2.5 08/15/2024 Govt` - US Treasury bond

### 4. Common Fields

**Reference Data Fields:**
- `NAME` - Security name
- `COUNTRY` - Country of incorporation
- `INDUSTRY_SECTOR` - Industry classification
- `CRNCY` - Currency
- `GICS_SECTOR_NAME` - GICS sector

**Market Data Fields:**
- `BID` - Best bid price
- `ASK` - Best ask price
- `LAST_PRICE` - Last trade price
- `VOLUME` - Trading volume
- `BID_SIZE` - Size at bid
- `ASK_SIZE` - Size at ask

### 5. Error Handling

In production code, you should handle:
- Authentication failures
- Service unavailability
- Invalid security identifiers
- Network disconnections
- Insufficient data entitlements
- Rate limiting

---

## Real-World Implementation Notes

### Dependencies
```bash
# Install Bloomberg API
pip install blpapi

# Or with uv
uv add blpapi
```

### Minimal Working Example
```python
import blpapi

# Session options
sessionOptions = blpapi.SessionOptions()
sessionOptions.setServerHost("bpipe-gateway.bloomberg.com")
sessionOptions.setServerPort(8194)

# Create and start session
session = blpapi.Session(sessionOptions)
if not session.start():
    print("Failed to start session")
    return

# Open service
if not session.openService("//blp/refdata"):
    print("Failed to open service")
    return

# Create request
refDataService = session.getService("//blp/refdata")
request = refDataService.createRequest("ReferenceDataRequest")
request.append("securities", "IBM US Equity")
request.append("fields", "PX_LAST")

# Send request and process events
session.sendRequest(request)
while True:
    event = session.nextEvent(500)
    # Process event...
    if event.eventType() == blpapi.Event.RESPONSE:
        break

session.stop()
```

### Performance Considerations

1. **Connection Pooling**: Reuse sessions across requests
2. **Bulk Requests**: Request multiple securities/fields in one call
3. **Subscription Management**: Only subscribe to needed securities
4. **Event Processing**: Use async/await or threading for event handling
5. **Rate Limiting**: Bloomberg imposes rate limits on API calls

---

## Additional Resources

- [Bloomberg API Documentation](https://www.bloomberg.com/professional/support/api-library/)
- [B-PIPE Product Page](https://www.bloomberg.com/professional/product/market-data-distribution/)
- [Bloomberg Developer Portal](https://www.bloomberg.com/professional/support/api/)
- Example code included in blpapi installation under `examples/` directory

---

## License

This is an educational illustration. Bloomberg B-PIPE is a commercial product requiring proper licensing and credentials from Bloomberg L.P.
