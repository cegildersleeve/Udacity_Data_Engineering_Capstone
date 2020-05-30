class SqlQueries:
    create_tables = ("""
        CREATE TABLE IF NOT EXISTS public.tweets (
            id varchar(256) NOT NULL,
            full_text text,
            user_id varchar(256),
            lang varchar(256),
            country_code varchar(256),
            latitude  float,
            longitude  float,
            "date" TIMESTAMP,
            rt integer,
            favourite_count integer,
            sentiment varchar(256),
            positive float,
            negative float,
            neutral float,
            mixed float,
            confirmed float,
            deaths float,
            recovered float,
            CONSTRAINT tweets_pkey PRIMARY KEY (id)
            );
        CREATE TABLE IF NOT EXISTS public.jhu (
            uid varchar(32) NOT NULL,
            fips varchar(256),
            iso2  varchar(256),
            iso3 varchar(256),
            code3 varchar(256),
            admin2 varchar(256),
            latitude float,
            longitude float,
            province_state varchar(256),
            country_region varchar(256),
            "date" date,
            confirmed float,
            deaths float,
            recovered float,
            country_code varchar(4),
        CONSTRAINT jhu_pkey PRIMARY KEY (uid)
        );
        CREATE TABLE IF NOT EXISTS public.gov (
            CountryName varchar(256),
            CountryCode varchar(4),
            "Date" date,
            C1_School_closing float,
            C1_Flag float,
            C1_Notes varchar(256),
            C2_Workplace_closing float,
            C2_Flag float,
            C2_Notes varchar(256),
            C3_Cancel_public_events float,
            C3_Flag float,
            C3_Notes varchar(256),
            C4_Restrictions_on_gatherings float,
            C4_Flag float,
            C4_Notes varchar(256),
            C5_Close_public_transport float,
            C5_Flag float,
            C5_Notes varchar(256),
            C6_Stay_at_home_requirements float,
            C6_Flag float,
            C6_Notes varchar(256),
            C7_Restrictions_on_internal_movement float,
            C7_Flag float,
            C7_Notes varchar(256),
            C8_International_travel_controls float,
            C8_Notes varchar(256),
            E1_Income_support float,
            E1_Flag float,
            E1_Notes varchar(256),
            "E2_Debt_contract_relief" varchar(256),
            E2_Notes varchar(256),
            E3_Fiscal_measures varchar(256),
            E3_Notes varchar(256),
            E4_International_support varchar(256),
            E4_Notes varchar(256),
            H1_Public_information_campaigns varchar(256),
            H1_Flag float,
            H1_Notes varchar(256),
            H2_Testing_policy float,
            H2_Notes varchar(256),
            H3_Contact_tracing float,
            H3_Notes varchar(256),
            H4_Emergency_investment_in_healthcare varchar(256),
            H4_Notes varchar(256),
            H5_Investment_in_vaccines varchar(256),
            H5_Notes varchar(256),
            M1_Wildcard varchar(256),
            M1_Notes varchar(256),
            ConfirmedCases float,
            ConfirmedDeaths float,
            StringencyIndex float,
            StringencyIndexForDisplay float,
            LegacyStringencyIndex float,
            LegacyStringencyIndexForDisplay float,
            country_code varchar(4),
        CONSTRAINT gov_pkey PRIMARY KEY (CountryCode, "Date")
        );
        CREATE TABLE IF NOT EXISTS public.user (
            user_id varchar(256) NOT NULL,
            handle varchar(256),
            description varchar(256),
            lang varchar(256),
            location varchar(256),
            friends float,
            followers integer,
            latitude float,
            longitude float,
            country_code varchar(4),
        CONSTRAINT user_pkey PRIMARY KEY (user_id)
        );
        CREATE TABLE IF NOT EXISTS time
        (   "date"    TIMESTAMP PRIMARY KEY sortkey distkey,
            hour          INTEGER,
            week          INTEGER,
            month         INTEGER,
            year          INTEGER,
            weekday       INTEGER
        );
        CREATE TABLE IF NOT EXISTS geo
        (
            latitude  float,
            longitude  float,
            country_code varchar(4),
            country varchar(256),
            state varchar(256),
            region varchar(256),
            province varchar(256),
            city varchar(256),
            postcode varchar(256),
            county varchar(256),
        CONSTRAINT geo_pkey PRIMARY KEY (latitude, longitude)
        );
        CREATE TABLE IF NOT EXISTS sentiment
        (
        id varchar(256) NOT NULL,
        full_text varchar(256),
        sentiment varchar(256),
        positive float,
        negative float,
        neutral float,
        mixed float,
        CONSTRAINT sentiment_pkey PRIMARY KEY (id)
        );
        CREATE TABLE IF NOT EXISTS public.staging_tweets (
        created_at TIMESTAMP,
        id varchar(256) NOT NULL,
        full_text varchar(256),
        "user" varchar(256),
        geo varchar(256),
        handle varchar(256),
        description varchar(256),
        coordinates varchar(256),
        place varchar(256),
        retweeted varchar(256),
        retweet_count integer,
        favorite_count integer,
        lang varchar(256),
        location varchar(256),
        friends integer,
        followers integer,
        source_url varchar(256),
        source_platform varchar(256),
        rt integer,
        geo_codes varchar(256),
        country varchar(256),
        country_code varchar(4),
        state varchar(256),
        region varchar(256),
        province varchar(256),
        city varchar(256),
        postcode varchar(256),
        county varchar(256),
        latitude float,
        longitude float,
        CONSTRAINT staging_tweets_pkey PRIMARY KEY (id)
        );
        """)
    geo_table_insert = ("""
        SELECT DISTINCT
        latitude,
        longitude,
        country_code,
        country,
        state,
        region,
        province,
        city,
        postcode,
        county
        FROM staging_tweets
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
    user_table_insert = ("""
        SELECT DISTINCT "user",
        handle,
        description,
        lang, location,
        friends,
        followers,
        latitude,
        longitude,
        country_code
        FROM staging_tweets;
        """)
    tweets_table_insert = ('''
        SELECT 	id,
		full_text,
		"user",
        lang,
        full_tweets.country_code,
        latitude,
        longitude,
        created_at,
        rt,
        favorite_count,
        sentiment,
        positive,
        negative,
        neutral,
        mixed,
        confirmed,
        deaths,
        recovered
        FROM (SELECT t.*,s.sentiment, s.positive, s.negative, s.neutral, s.mixed
        FROM staging_tweets t
        LEFT JOIN sentiment s
        ON t.id = s.id) full_tweets
        LEFT JOIN
        (Select "date", country_code, sum(confirmed) "confirmed", sum(deaths) "deaths", sum(recovered)"recovered"
        FROM jhu
        GROUP BY "date", country_code)jhu
        ON Date(full_tweets.created_at)=jhu.Date
        AND full_tweets.country_code=jhu.country_code;'''
        )
    time_table_insert = ('''
        SELECT DISTINCT created_at,
           extract(hour from created_at),
           extract(week from created_at),
           extract(month from created_at),
           extract(year from created_at),
           extract(dayofweek from created_at)
           FROM staging_tweets;'''
           )
