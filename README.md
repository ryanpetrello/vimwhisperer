# vimwhisperer

A simple Vim plugin for AWS CodeWhisperer code completion support.

## Configuration and Authentication

Install this Python package, e.g.,

```
    ~ pip3 install --user git+https://github.com/ryanpetrello/vimwhisperer.git
```

If necessary, set the following environment variables:

```
    ~ export VIM_AWS_SSO_START_URL='https://my-example-app.awsapps.com/start'
    ~ export VIM_AWS_SSO_REGION='us-west-2'
```

Authenticate for the first time using AWS IAM Identity Center.

An OIDC client and Bearer token will be generated, and will be cached at ``~/.vim/.aws-code-whisperer-auth`` for subsequent API calls:

```
    ~ python -m vimwhisperer.login
```

## Running Code Completion by Hand

```python
    ~ echo 'def read_from_s3(bucket, key):' | python -m vimwhisperer
        import boto3
        s3 = boto3.resource('s3')
        obj = s3.Object(bucket, key)
        return obj.get()['Body'].read().decode('utf-8')
```

## Installing the Vim Plugin

Install ``vimwhisperer.vim`` using your plugin manager, and map to the leader key of your choosing, i.e.,

```
    map <Leader>a :silent! call CodeWhisperer()<CR>
```

https://github.com/ryanpetrello/vimwhisperer/assets/214912/e13aadf7-8409-4325-be4f-6d9bff8bb945


