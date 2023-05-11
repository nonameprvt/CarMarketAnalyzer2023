from avito import get_parsed_avito, CaptchaException

should_parse_big_brands = True
brand_to_start = None
model_to_start = None

while True:
    if brand_to_start is None:
        should_parse_big_brands = not should_parse_big_brands
    try:
        get_parsed_avito(should_parse_big_brands, brand_to_start, model_to_start)
        brand_to_start = None
        model_to_start = None
    except CaptchaException as e:
        print(e)
        if should_parse_big_brands:
            model_to_start = str(e).split(';')[1]
        brand_to_start = str(e).split(';')[0]
