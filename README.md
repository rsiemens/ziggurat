# Ziggurat

A simple and straightforward Python templating engine.

```
Dunder Mifflin Sales Report
---------------------------

{ branch | capitalize} - {quarter} {year}

@if confidential@
Private Information, do not share!
@endif@

Product    Sold    Amount
@for product in sales@
{product.name}  {product.sold}  {product.amount | with_dollar_sign}
@endfor@
```

```python
from ziggurat import Template, register_transform

@register_transform
def with_dollar_sign(value):
    return f'${value}'

report = Template('report.txt').render({
    'branch': 'scranton',
    'quarter': 'Q1',
    'year': 2021,
    'confidential': True,
    'sales': [
        {'name': 'Letter 8.5" x 11"', 'sold': 500, 'amount': 8975},
        {'name': 'Legal 8.5" x 14"', 'sold': 237, 'amount': 7107},
    ]
})

print(report)
```

```
Dunder Mifflin Sales Report
---------------------------

Scranton - Q1 2021

Private Information, do not share!

Product    Sold    Amount
Letter 8.5" x 11"  500  $8975
Legal 8.5" x 14"  237  $7107
```
