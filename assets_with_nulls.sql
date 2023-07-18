SELECT *
FROM assets
WHERE 
    sector IS NULL or sector = '' or
    business_summary IS NULL or business_summary = '' or
    name IS NULL or name = '' or
    number_of_shares IS NULL or number_of_shares = '' or
    website IS NULL or website = '' or
    industry IS NULL or industry = ''