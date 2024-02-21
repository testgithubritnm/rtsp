# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views import View
# from zeep import Client




# class MyServiceView(View, DefinitionBase):
#     @rpc(String, _returns=String)
#     def my_method(self, input_string):
#         return 'Hello, ' + input_string
# class MySoapServiceView(View):
#     def get(self, request):
#         try:
#             # Load the WSDL file
#             wsdl_url = 'http://example.com/myservice.wsdl'
#             client = Client(wsdl_url)

#             # Call operations defined in the WSDL
#             response = client.service.MyOperation(input_data)

#             # Process the response
#             return JsonResponse({'response': response})

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)