swagger_config={
    "headers":[],
    "specs":[
        {
        "endpoint":"apispec_1",
        "route":"/api/docs/swagger.json",
        "rule_filter":lambda rule:True,
        "model_filter":lambda tag:True
        }
    ],
    "static_url_path":"/flasgger_static",
    "specs_route":"/api/docs",
    "swagger_ui":True
}