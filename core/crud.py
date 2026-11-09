import re
from functools import reduce
from operator import or_

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.urls import path, reverse
from django.views.generic import ListView

CODE_RE = re.compile(r"^([a-z]+)-?(\d+)$", re.IGNORECASE)


class ListPage(LoginRequiredMixin, ListView):
    """Paginated list page; an out-of-range ?page= shows the last page."""

    paginate_by = 10
    ordering = ["-id"]
    page_title = ""
    add_label = ""
    url_name = ""
    search_fields = []  # text columns, e.g. ["first_name", "member__last_name"]
    search_codes = {}  # code prefix -> column, e.g. {"MEM": "pk", "STF": "staff_id"}
    search_hint = ""

    def get_search_term(self):
        return self.request.GET.get("q", "").strip()

    def search(self, queryset, term):
        """Every word must match some field or code; words are ANDed."""
        for word in term.split():
            clauses = [Q(**{f"{f}__icontains": word}) for f in self.search_fields]
            match = CODE_RE.match(word)
            column = match and self.search_codes.get(match[1].upper())
            if column:
                clauses.append(Q(**{column: int(match[2])}))
            elif word.isdigit():
                clauses.append(Q(pk=int(word)))
            if clauses:
                queryset = queryset.filter(reduce(or_, clauses))
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        term = self.get_search_term()
        return self.search(queryset, term) if term else queryset

    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        page = paginator.get_page(self.request.GET.get(self.page_kwarg))
        return paginator, page, page.object_list, page.has_other_pages()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["add_label"] = self.add_label
        context["q"] = self.get_search_term()
        context["search_hint"] = self.search_hint
        context["add_url"] = reverse(f"{self.url_name}_add")
        return context


class ModalFormMixin(LoginRequiredMixin):
    """Create/update views shown in a modal; success answers 204."""

    template_name = "partials/_modal_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object is None:
            title = f"Add {self.model._meta.verbose_name}"
        else:
            title = f"Edit {self.object.code}"
        context["modal_title"] = title
        return context

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, f"{self.object.code} saved")
        return HttpResponse(status=204)

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form), status=400
        )


class ModalDeleteMixin(LoginRequiredMixin):
    """Delete confirmation shown in a modal; success answers 204."""

    template_name = "partials/_modal_delete.html"
    delete_note = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["delete_note"] = self.delete_note
        return context

    def form_valid(self, form):
        code = self.object.code
        self.object.delete()
        messages.success(self.request, f"{code} deleted")
        return HttpResponse(status=204)


def crud_urls(prefix, name, list_view, create_view, update_view, delete_view):
    """URL entries <prefix>/, add/, <pk>/edit/, <pk>/delete/ named <name>_*."""
    prefix = prefix.strip("/") + "/"
    return [
        path(prefix, list_view.as_view(), name=f"{name}_list"),
        path(f"{prefix}add/", create_view.as_view(), name=f"{name}_add"),
        path(
            f"{prefix}<int:pk>/edit/",
            update_view.as_view(),
            name=f"{name}_edit",
        ),
        path(
            f"{prefix}<int:pk>/delete/",
            delete_view.as_view(),
            name=f"{name}_delete",
        ),
    ]
