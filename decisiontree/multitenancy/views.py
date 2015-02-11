from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_text

from .utils import multitenancy_enabled


class TenantViewMixin(object):
    """Mixin for generic class-based views to handle tenant-enabled objects.

    Use with:
        * ListView
        * DetailView
        * CreateView
        * UpdateView
        * DeleteView
    """
    success_url_name = None

    def dispatch(self, request, *args, **kwargs):
        """Attach the tenant and group to the class."""
        if multitenancy_enabled():
            from multitenancy.auth import get_user_groups, get_user_tenants
            available_groups = get_user_groups(request.user)
            self.group = get_object_or_404(available_groups, slug=kwargs['group_slug'])
            available_tenants = get_user_tenants(request.user, self.group)
            self.tenant = get_object_or_404(available_tenants, slug=kwargs['tenant_slug'])
        else:
            self.group = None
            self.tenant = None
        return super(TenantViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add the tenant and group to the template context."""
        kwargs['group'] = self.group
        kwargs['tenant'] = self.tenant
        return super(TenantViewMixin, self).get_context_data(**kwargs)

    def get_queryset(self):
        """Limit queryset based on tenant if multitenancy is enabled."""
        qs = super(TenantViewMixin, self).get_queryset()
        if multitenancy_enabled():
            if not hasattr(self.model, 'tenantlink'):
                raise ImproperlyConfigured("TenantViewMixin can only be used "
                                           "with tenant-enabled models.")
            qs = qs.filter(tenantlink__tenant=self.tenant)
        return qs

    def get_success_url(self, *args, **kwargs):
        """Add group and tenant slugs to URL resolution if multitenancy is enabled."""
        if self.success_url:
            return force_text(self.success_url)
        if self.success_url_name:
            if multitenancy_enabled():
                if args:
                    args = (self.group.slug, self.tenant.slug) + args
                else:
                    kwargs['group_slug'] = self.group.slug
                    kwargs['tenant_slug'] = self.tenant.slug
            return reverse(self.success_url_name, args=args, kwargs=kwargs)
        raise ImproperlyConfigured("No URL to redirect to. Provide a "
                                   "success_url or success_url_name.")
