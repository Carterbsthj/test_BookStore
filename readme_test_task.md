== COMMENTS ==

Need to create task solution (API) and put it to github or gitlab account (public or private with my user access to it)
You can choose by yourself frameworks (API, ORM, DB driver etc)

DB should be SQL (no matter what kind of DB)
You choose table structure as you want. Here you can find business issue without table names, primary keys etc

Response HTTP codes: 
200 - OK
201 - Created (for POST requests)
422 - wrong request structure
404 - Entity not found (when we have "key" in request)
404 - Wrong endpoint
500 - server error


P.S. No need to check time zone. User and server have same time zone and we don't need to convert it
P.S.2 Choose simple way if something not clear in this task or just ask me

== TASK ==

Create REST API

We have few bookshops. And now we want to create app for books storing.
We already have frontend team, and we need server part.

What we have: 
Books: title, publish year, author, barcode
Authors: name, birth date
Storing information: "book", "quantity"

Books: barcode can change, title can be same for different publish years, author - foreign field for Author table (we have one author for a book)
We will search books by barcode most of the time.

Authors: name can be same for different birth dates

Storing information: book - foreign field for books table, quantity - number of books that we have
We need to get history of storing information


== ENDPOINTS == 

Ping
    
    GET /ping

Authors
     
    add
        POST /author
        {
            name, # string, mandatory
            birth_date # string YYYY-MM-DD, Grater than 01/01/1900, mandatory
        }
        response: 201, {"key"} # key - primary key

    get
        GET /author/{key}
        {
            "key", # key - primary key
            "name"
        }


Books
    add
        
    POST /book
        {
            "barcode", # string, can be not filled
            "title", # string, mandatory
            "publish_year", # integer (bigger than 1900), mandatory
            "author" # foreign field, mandatory,
        }

    get
        GET /book/{key}
        {
            "key", 
            "barcode", 
            "title",
            "publish_year",
            "author": {"name", birth_date},
            "quantity" # from storing table
        }

    search by barcode (sort by barcode), can be not equal (start of string, so for barcode=23 need to be found bookd with barcodes: 23,235,239,23AS etc)
        GET /book?barcode=...
        {
            "found", # count of found items
            "items": [
                {
                    "key", 
                    "barcode", 
                    "title",
                    "publish_year",
                    "author": {"name", birth_date},
                    "quantity" 
                }, ...
            ]
        }

STORING
    add
        
        POST /leftover/add
        POST /leftover/remove
        {
            "barcode", # book barcode, mandatory
            "quantity" # int, grater than 0
        }

        POST /leftovers/bulk # save leftovers from excel ot txt file
        EXCEL: there will be 1 page and first column will be "barcode" and second quantity (+/-)
        Need to upload data from file 
        - if barcode = "" - it is not error, just skip this row
        - if barcode is filled but no data in our base - error 404 (with info of row number)
        - if quantity not a number - error 400 (with info of row)

        TXT:
        Strings starts with type of string (3 chars) and ends with CR LF / LF
        "BRC" - barcode
        "QNT" - quantity

        File text example:
        FLN15
        ITC3
        ITN1
        BRC15110
        QNT2
        ITN2
        BRC15002
        QNT-3
        ITN3
        BRC14810
        QNT3
        ITT3

        if we have error - no data need to uploaded
 



== TESTS == 
Need to add few functional testing
3-4 variants to add books endpoint
3-4 variants to get books endpoint

== Changes ==

search by barcode (sort by barcode), can be not equal (start of string, so for barcode=23 need to be found bookd with barcodes: 23,235,239,23AS etc)

Modify prev app
Remove 
POST /leftover

add endpoints:
    POST /leftover/add
    POST /leftover/remove
        With body: 
                {
                    "barcode", # book barcode, mandatory
                    "quantity" # int, grater than 0
                }

    Example, book "One" with quantity = 1
    add 5, now quantity = 6
    remove 3, now quantity = 3


    POST /leftovers/bulk # save leftovers from excel ot txt file
        EXCEL: there will be 1 page and first column will be "barcode" and second quantity (+/-)
        Need to upload data from file 
        - if barcode = "" - it is not error, just skip this row
        - if barcode is filled but no data in our base - error 404 (with info of row number)
        - if quantity not a number - error 400 (with info of row)

        TXT:
        Strings starts with type of string (3 chars) and ends with CR LF / LF
        "BRC" - barcode
        "QNT" - quantity

        File text example:
        FLN15
        ITC3
        ITN1
        BRC15110
        QNT2
        ITN2
        BRC15002
        QNT-3
        ITN3
        BRC14810
        QNT3
        ITT3

        if we have error - no data need to uploaded

And change history endpoint
    history
        
        GET /history?start={YYYY-MM-DD}&end={YYYY-MM-DD}&book={key}
        start and end - period parameters
        all parameters are optional
        [{
                    "book": {"key", "title", "barcode"},
                    "start_balance", # leftovers on start date
                    "end_balance",  # leftovers on end date
                    "history": [ # need to be sort by date DESC
                        {
                            "date", # date of row creation
                            "quantity" # + or - depends on add or remove endpoint
                        }
                    ]
                }]


