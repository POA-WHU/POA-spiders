# POA-spiders
Web spiders used in Public Opinions Analysis

## Tested Environment
> + Windows 10 Pro 64-bit 20H2
> + python 3.9.2

## Dependencies
```commandline
pip install -r requirements.txt
```

## How to build new Spider
Inherit `BaseURLManager` and `BaseSpider` from `base` package, then overwrite their `parse()` methods.

`BaseURLManager.parse()` receives the page count of a catalog and returns document urls on that catalog page.

`BaseSpider.parse()` receives a document url and returns useful content on that document page.

