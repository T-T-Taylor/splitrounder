Files for splitrounder backend server

To run put all files in dir and add .json files for config, contact_ids, and purchased
See files for required python imports

Other Dependancies
- Requires an acive GHL account with 2.0 API access
- Contacts in the GHL account must be formated as expected by the program
- If using a GHL account that is not the official splitrounder account, some hard coded reference ID's will need to be updated for proper function

Known Problems
- There is a loop in the sell function that was never resolved
- Logic for triggering purchase is not fool proof (requires some limited babysitting)
- Has some glitches when running on windows (only fully functinal on linux syestems)

Note: splitrounder is made to connect to robinhood brokerage accounts, as of October 2024 robinhood appeared to stop allowing users to collect fractinal shares that had rounded up (stopped delivering the shares to users accounts after a split had taken place).
Note: Retired from official use in Nov 2024
