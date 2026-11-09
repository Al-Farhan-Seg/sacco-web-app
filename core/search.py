import re
from functools import reduce
from operator import or_

from django.db.models import Q

CODE_RE = re.compile(r"^([a-z]+)-?(\d+)$", re.IGNORECASE)


def search(queryset, term, fields, codes):
    """Narrow a queryset to the rows that match what was typed in a search box.

    term   - the text typed, e.g. "john mukasa" or "mem-7"
    fields - text columns searched with "contains", e.g. ["first_name", "member__last_name"]
    codes  - code prefix -> column, so "MEM-007" finds member 7, e.g. {"MEM": "pk"}

    Every word must match something (words are ANDed); a word may match any field (ORed).
    """
    for word in term.split():
        clauses = [Q(**{f"{field}__icontains": word}) for field in fields]
        match = CODE_RE.match(word)
        column = match and codes.get(match[1].upper())
        if column:
            clauses.append(Q(**{column: int(match[2])}))
        elif word.isdigit():
            clauses.append(Q(pk=int(word)))
        if clauses:
            queryset = queryset.filter(reduce(or_, clauses))
    return queryset
