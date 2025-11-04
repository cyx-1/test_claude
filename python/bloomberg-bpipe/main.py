"""
Bloomberg B-PIPE API Illustration

This example demonstrates how to use Bloomberg's B-PIPE (Bloomberg Pipe) API to:
1. Authenticate with Bloomberg (both application and user authentication)
2. Retrieve reference data (static security information)
3. Subscribe to real-time market data (price updates)

Note: This code requires the blpapi package and valid Bloomberg credentials.
It will not run without access to Bloomberg infrastructure.
"""

import datetime
import time
from typing import Optional


# Note: In a real implementation, you would import:
# import blpapi
# For this illustration, we'll simulate the blpapi module structure


class BloombergBPipeClient:
    """
    Illustrates Bloomberg B-PIPE API usage patterns.

    B-PIPE supports two authentication modes:
    1. Application Authentication: The application itself is authenticated
    2. User Authentication: Individual users are authenticated (more restrictive)
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8194,
        app_name: Optional[str] = None,
        user_auth_required: bool = False,
    ):
        """
        Initialize Bloomberg B-PIPE client.

        Args:
            host: Bloomberg gateway host (default: localhost for desktop, or specific server for B-PIPE)
            port: Bloomberg gateway port (8194 for B-PIPE, 8194 for Desktop API)
            app_name: Application name for authentication (e.g., "MyTradingApp")
            user_auth_required: Whether user authentication is required
        """
        self.host = host
        self.port = port
        self.app_name = app_name
        self.user_auth_required = user_auth_required
        self.session = None

        # Line 54: Session options configuration
        print(f"\n{'='*80}")
        print("STEP 1: CONFIGURING SESSION OPTIONS")
        print(f"{'='*80}")
        print(f"[Line 54-59] Setting up connection parameters:")
        print(f"  • Host: {self.host}")
        print(f"  • Port: {self.port}")
        print(f"  • Application Name: {self.app_name or 'Not specified'}")
        print(f"  • User Authentication Required: {self.user_auth_required}")

    def authenticate_application(self) -> bool:
        """
        Line 66-85: Application authentication.

        Application authentication allows the entire application to access Bloomberg data.
        This is typically used for server-based applications where the app itself is trusted.
        """
        print(f"\n{'='*80}")
        print("STEP 2: APPLICATION AUTHENTICATION")
        print(f"{'='*80}")

        if not self.app_name:
            print("[Line 77] No application name provided - skipping app authentication")
            return True

        print(f"[Line 80] Authenticating application: {self.app_name}")
        print("[Line 81] Sending authentication token request...")
        print("[Line 82] Waiting for authentication response...")

        # Simulated authentication response
        print(f"[Line 85] ✓ Application '{self.app_name}' authenticated successfully")
        return True

    def authenticate_user(self, user_id: str, ip_address: str) -> bool:
        """
        Line 88-110: User authentication.

        User authentication is more restrictive and ties data access to specific users.
        This is required when you need to track individual user access or when
        Bloomberg licensing requires per-user authentication.

        Args:
            user_id: Bloomberg UUID or user identifier
            ip_address: IP address of the user's workstation
        """
        print(f"\n{'='*80}")
        print("STEP 3: USER AUTHENTICATION")
        print(f"{'='*80}")

        if not self.user_auth_required:
            print("[Line 104] User authentication not required - skipping")
            return True

        print(f"[Line 107] Authenticating user: {user_id}")
        print(f"[Line 108] User IP address: {ip_address}")
        print("[Line 109] Sending user authentication request...")

        # Simulated authentication response
        print(f"[Line 110] ✓ User '{user_id}' authenticated successfully")
        return True

    def open_services(self):
        """
        Line 113-135: Opening Bloomberg services.

        B-PIPE provides different services for different data types:
        - //blp/refdata: Reference data (static security information)
        - //blp/mktdata: Market data (real-time prices and updates)
        - //blp/instruments: Instrument lookup and search
        """
        print(f"\n{'='*80}")
        print("STEP 4: OPENING BLOOMBERG SERVICES")
        print(f"{'='*80}")

        services = [
            "//blp/refdata",  # Reference Data Service
            "//blp/mktdata",  # Market Data Service
        ]

        for service in services:
            print(f"[Line 130] Opening service: {service}")
            # In real implementation: self.session.openService(service)
            print(f"[Line 132] ✓ Service '{service}' opened successfully")

        print("[Line 135] All required services are now available")

    def request_reference_data(self, securities: list[str], fields: list[str]):
        """
        Line 138-195: Request reference data.

        Reference data contains static or slowly-changing information about securities:
        - Company fundamentals
        - Security descriptions
        - Credit ratings
        - Corporate actions

        Args:
            securities: List of security identifiers (e.g., ["IBM US Equity", "AAPL US Equity"])
            fields: List of data fields to retrieve (e.g., ["PX_LAST", "NAME", "COUNTRY"])
        """
        print(f"\n{'='*80}")
        print("STEP 5: REQUESTING REFERENCE DATA")
        print(f"{'='*80}")

        print(f"[Line 157] Creating reference data request")
        print(f"[Line 158] Securities: {securities}")
        print(f"[Line 159] Fields: {fields}")

        # In real implementation:
        # refDataService = self.session.getService("//blp/refdata")
        # request = refDataService.createRequest("ReferenceDataRequest")
        # for security in securities:
        #     request.append("securities", security)
        # for field in fields:
        #     request.append("fields", field)

        print(f"[Line 169] Sending request to //blp/refdata service...")
        print(f"[Line 170] Waiting for response...\n")

        # Simulated response
        print("="*80)
        print("REFERENCE DATA RESPONSE")
        print("="*80)

        for security in securities:
            print(f"\n[Line 178] Security: {security}")
            print(f"[Line 179] {'─'*60}")

            if "IBM" in security:
                print(f"[Line 181]   PX_LAST        = 147.52")
                print(f"[Line 182]   NAME           = INTERNATIONAL BUSINESS MACHINES CORP")
                print(f"[Line 183]   COUNTRY        = US")
                print(f"[Line 184]   INDUSTRY_SECTOR = Technology")
                print(f"[Line 185]   LAST_UPDATE    = 2024-10-31 16:00:00")
            elif "AAPL" in security:
                print(f"[Line 187]   PX_LAST        = 225.91")
                print(f"[Line 188]   NAME           = APPLE INC")
                print(f"[Line 189]   COUNTRY        = US")
                print(f"[Line 190]   INDUSTRY_SECTOR = Technology")
                print(f"[Line 191]   LAST_UPDATE    = 2024-10-31 16:00:00")

        print(f"\n[Line 195] ✓ Reference data request completed")

    def subscribe_market_data(self, securities: list[str], fields: list[str]):
        """
        Line 198-280: Subscribe to real-time market data.

        Market data subscriptions provide continuous updates for:
        - Real-time prices (BID, ASK, LAST)
        - Trading volume
        - Market depth
        - Trade ticks

        Once subscribed, updates are pushed to the client as they occur.

        Args:
            securities: List of security identifiers to subscribe to
            fields: List of fields to monitor (e.g., ["BID", "ASK", "LAST_PRICE"])
        """
        print(f"\n{'='*80}")
        print("STEP 6: SUBSCRIBING TO REAL-TIME MARKET DATA")
        print(f"{'='*80}")

        print(f"[Line 217] Creating market data subscription")
        print(f"[Line 218] Securities: {securities}")
        print(f"[Line 219] Fields: {fields}")

        # In real implementation:
        # subscriptions = blpapi.SubscriptionList()
        # for security in securities:
        #     subscriptions.add(security, fields, "", blpapi.CorrelationId(security))
        # self.session.subscribe(subscriptions)

        print(f"[Line 227] Subscription request sent to //blp/mktdata service")
        print(f"[Line 228] Subscription active - will receive updates as they occur\n")

        # Simulate receiving market data updates
        print("="*80)
        print("REAL-TIME MARKET DATA UPDATES")
        print("="*80)

        # Simulate initial snapshot
        print(f"\n[Line 236] ─── SUBSCRIPTION SNAPSHOT (Initial Data) ───")
        print(f"[Line 237] Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

        for security in securities:
            print(f"\n[Line 240] {security}:")
            if "IBM" in security:
                print(f"[Line 241]   BID        = 147.48")
                print(f"[Line 242]   ASK        = 147.52")
                print(f"[Line 243]   LAST_PRICE = 147.50")
                print(f"[Line 244]   VOLUME     = 3,245,678")
            elif "AAPL" in security:
                print(f"[Line 246]   BID        = 225.88")
                print(f"[Line 247]   ASK        = 225.92")
                print(f"[Line 248]   LAST_PRICE = 225.90")
                print(f"[Line 249]   VOLUME     = 45,678,901")

        # Simulate several real-time updates
        updates = [
            {
                "time_offset": 1.5,
                "security": securities[0],
                "changes": {"LAST_PRICE": 147.53, "VOLUME": 3_246_100},
            },
            {
                "time_offset": 2.3,
                "security": securities[1] if len(securities) > 1 else securities[0],
                "changes": {"BID": 225.89, "ASK": 225.93, "LAST_PRICE": 225.91},
            },
            {
                "time_offset": 3.1,
                "security": securities[0],
                "changes": {"BID": 147.50, "ASK": 147.54, "LAST_PRICE": 147.52},
            },
        ]

        for idx, update in enumerate(updates, 1):
            print(f"\n[Line {260 + idx*5}] ─── UPDATE #{idx} ───")
            print(
                f"[Line {261 + idx*5}] Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}"
            )
            print(f"[Line {262 + idx*5}] Security: {update['security']}")
            print(f"[Line {263 + idx*5}] Changes:")
            for field, value in update["changes"].items():
                if field == "VOLUME":
                    print(f"[Line {264 + idx*5}]   {field:12} = {value:,}")
                else:
                    print(f"[Line {264 + idx*5}]   {field:12} = {value:.2f}")

        print(f"\n[Line 280] ✓ Market data subscription active (press Ctrl+C to stop)")

    def close_session(self):
        """
        Line 283-293: Clean up and close the session.

        Proper cleanup ensures:
        - All subscriptions are cancelled
        - Network connections are closed
        - Resources are freed
        """
        print(f"\n{'='*80}")
        print("STEP 7: CLOSING SESSION")
        print(f"{'='*80}")

        print("[Line 292] Closing Bloomberg session...")
        print("[Line 293] ✓ Session closed successfully")


def main():
    """
    Main function demonstrating Bloomberg B-PIPE workflows.

    This example shows two common scenarios:
    1. Application-authenticated access (lines 302-330)
    2. User-authenticated access (lines 333-360)
    """
    print("\n" + "="*80)
    print(" BLOOMBERG B-PIPE API ILLUSTRATION")
    print("="*80)

    # ========================================================================
    # SCENARIO 1: Application Authentication
    # ========================================================================
    print("\n" + "█"*80)
    print("█ SCENARIO 1: APPLICATION AUTHENTICATION MODE")
    print("█"*80)
    print("""
[Line 316-320] In this mode:
  • The application authenticates with Bloomberg using its app name
  • All users of the application share the same data entitlements
  • Typically used for server-based applications (web servers, analytics engines)
  • Requires Bloomberg to register your application name
    """)

    # Line 325: Initialize client with application authentication
    client1 = BloombergBPipeClient(
        host="bpipe-gateway.bloomberg.com",
        port=8194,
        app_name="MyTradingApp",
        user_auth_required=False,
    )

    # Line 333: Authenticate the application
    client1.authenticate_application()

    # Line 336: Open required services
    client1.open_services()

    # Line 339: Request reference data
    client1.request_reference_data(
        securities=["IBM US Equity", "AAPL US Equity"],
        fields=["PX_LAST", "NAME", "COUNTRY", "INDUSTRY_SECTOR", "LAST_UPDATE"],
    )

    # Line 345: Subscribe to real-time market data
    client1.subscribe_market_data(
        securities=["IBM US Equity", "AAPL US Equity"],
        fields=["BID", "ASK", "LAST_PRICE", "VOLUME"],
    )

    # Line 351: Close session
    client1.close_session()

    # ========================================================================
    # SCENARIO 2: User Authentication
    # ========================================================================
    print("\n\n" + "█"*80)
    print("█ SCENARIO 2: USER AUTHENTICATION MODE")
    print("█"*80)
    print("""
[Line 362-367] In this mode:
  • Individual users authenticate with their Bloomberg credentials
  • Each user has their own data entitlements based on their Bloomberg subscription
  • Typically required for:
    - Desktop applications where multiple users log in
    - Compliance requirements tracking individual user access
    - Bloomberg licensing that requires per-user authentication
    """)

    # Line 372: Initialize client with user authentication
    client2 = BloombergBPipeClient(
        host="bpipe-gateway.bloomberg.com",
        port=8194,
        app_name="MyTradingApp",
        user_auth_required=True,
    )

    # Line 380: Authenticate the application first
    client2.authenticate_application()

    # Line 383: Then authenticate the specific user
    client2.authenticate_user(
        user_id="john.doe@example.com",
        ip_address="192.168.1.100",
    )

    # Line 389: Open required services
    client2.open_services()

    # Line 392: Request reference data (with user entitlements)
    client2.request_reference_data(
        securities=["MSFT US Equity", "GOOGL US Equity"],
        fields=["PX_LAST", "NAME", "COUNTRY", "INDUSTRY_SECTOR"],
    )

    # Line 398: Subscribe to real-time market data (with user entitlements)
    client2.subscribe_market_data(
        securities=["MSFT US Equity"],
        fields=["BID", "ASK", "LAST_PRICE"],
    )

    # Line 404: Close session
    client2.close_session()

    # Summary
    print("\n\n" + "="*80)
    print(" SUMMARY: KEY DIFFERENCES")
    print("="*80)
    print("""
[Line 411-422] Application vs User Authentication:

APPLICATION AUTH:
  ✓ Simpler setup - one authentication for entire app
  ✓ Better for server-side applications
  ✓ All users share same data entitlements
  ✗ Cannot track individual user access
  ✗ May not meet compliance requirements

USER AUTH:
  ✓ Individual user entitlements enforced
  ✓ Audit trail of user access
  ✓ Meets compliance requirements
  ✗ More complex - must authenticate each user
  ✗ Additional latency for user authentication
    """)


if __name__ == "__main__":
    main()
