from typing import Dict, Literal, TypedDict

from django.http import HttpRequest
from django.shortcuts import render
from django_htmx.http import HttpResponseClientRefresh
from rest_framework import status, viewsets
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response

type ViewSetMethod = (
    Literal["retrieve"]
    | Literal["create"]
    | Literal["create-success"]
    | Literal["update"]
)


class HtmxTemplateDict(TypedDict):
    name: str


def htmx_response(
    request,
    method: ViewSetMethod,
    viewset_instance: "HTMXModelViewSet",
    serializer,
    model_instance=None,
):
    if not request.htmx:
        return None

    # Forego any further processing on client refresh
    if "Hx-Refresh" in request.headers and serializer.is_valid():
        return HttpResponseClientRefresh()

    template = viewset_instance.htmx_templates.get(method, "")
    if not template:
        return None

    return render(
        request,
        template["name"],
        {"serializer": serializer, "data": model_instance},
    )


class HTMXModelViewSet(viewsets.ModelViewSet):
    """
    A helper class that allows to supply a template path
    to be rendered as a response to an HTMX request to DRF

    This exists only for convenience and is not meant to handle complex cases
    For such cases it would most likely be more productive to inherit
    one of DRF's viewsets instead of this one.

    Property htmx_templates is a dict that maps restful actions to an HtmxTemplateDict

    dict[HtmxTemplateDict]:
    :name - The name of/path to the template, i.e. "users/detail.html"
    """

    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    htmx_templates: Dict[ViewSetMethod, HtmxTemplateDict]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return htmx_response(
            request, "retrieve", self, serializer, instance
        ) or Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=not request.htmx):
            instance = serializer.save()
        else:
            return htmx_response(request, "retrieve", self, serializer, instance)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return htmx_response(request, "update", self, serializer, instance) or Response(
            serializer.data
        )

    def create(self, request: HttpRequest, *args, **kwargs):
        instance = None
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=not request.htmx):
            instance = serializer.save()
        else:
            return htmx_response(request, "create", self, serializer)

        return htmx_response(
            request, "create-success", self, serializer, instance
        ) or Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )
