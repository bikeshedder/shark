from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from . import models


@permission_required('sepa.change_directdebitbatch')
def sepa_xml(self, pk):
    dd_batch = get_object_or_404(models.DirectDebitBatch, pk=pk)
    response = HttpResponse(dd_batch.render_sepa_xml(), content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=SEPA_DD_%s.xml' % dd_batch.uuid
    return response
