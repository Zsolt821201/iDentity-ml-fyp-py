label = {
    'location_label': '#my-desc',
    'sign_in_label': '.container h2'
}
header = {
    'header_links': '.navbar-nav .nav-item .nav-link'
}
table = {
    "content": '.table tbody tr'
}


def table_rows(position):
    return f'.table tbody tr:nth-of-type({position})'


def row_positions(row, position):
    return f'.table tbody tr:nth-of-type({row}) td:nth-of-type({position})'
