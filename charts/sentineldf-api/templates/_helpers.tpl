{{- define "sentineldf-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "sentineldf-api.fullname" -}}
{{- printf "%s" (include "sentineldf-api.name" .) -}}
{{- end -}}

{{- define "sentineldf-api.labels" -}}
app.kubernetes.io/name: {{ include "sentineldf-api.name" . }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/instance: {{ .Release.Name | default "sentineldf-api" }}
app.kubernetes.io/managed-by: Helm
{{- end -}}

{{- define "sentineldf-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "sentineldf-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name | default "sentineldf-api" }}
{{- end -}}
