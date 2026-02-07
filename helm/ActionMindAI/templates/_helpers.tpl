{{/*
Expand the name of the chart.
*/}}
{{- define "ActionMindAI.name" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "ActionMindAI.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ActionMindAI.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ActionMindAI.labels" -}}
helm.sh/chart: {{ include "ActionMindAI.chart" . }}
{{ include "ActionMindAI.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ActionMindAI.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ActionMindAI.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "ActionMindAI.frontendLabels" -}}
{{ include "ActionMindAI.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Backend labels
*/}}
{{- define "ActionMindAI.backendLabels" -}}
{{ include "ActionMindAI.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
ServiceAccount name
*/}}
{{- define "ActionMindAI.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ActionMindAI.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Migration labels
*/}}
{{- define "ActionMindAI.migrationLabels" -}}
{{ include "ActionMindAI.labels" . }}
app.kubernetes.io/component: migration
{{- end }}
