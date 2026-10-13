import { createFileRoute } from '@tanstack/react-router';
import {
	Button,
	Card,
	Divider,
	Drawer,
	Input,
	Space,
	Switch,
	Tag,
	Typography,
	Select,
	message,
	type InputRef
} from 'antd';
import { useEffect, useRef, useState } from 'react';

export const Route = createFileRoute('/config')({ component: Config });

type ClassificationRules = {
	direct_applicant_types: string[];
	ic_postal_prefixes: string[];
};
type Configuration = {
	classification_rules: ClassificationRules;
	field_mapping: Record<string, string[]>;
	settings_path: string;
	settings_dir: string;
	mailable_conditions: MailableCondition[];
	nurture: {
		file_path: string;
		report_field: string;
		nurture_header: string;
		enable: boolean;
	};
};
type MailableCondition = {
	key: string;
	label: string;
	field: string;
	mode: string;
	enabled: boolean;
	values: string[];
};
const emptyRules: ClassificationRules = {
	direct_applicant_types: [],
	ic_postal_prefixes: []
};

function EditableValues(props: {
	values: string[];
	onChange: (values: string[]) => void;
	placeholder: string;
	columns?: number;
}) {
	const add = () => props.onChange([...props.values, '']);
	const update = (index: number, value: string) => {
		const values = [...props.values];
		values[index] = value;
		props.onChange(values);
	};
	const remove = (index: number) =>
		props.onChange(
			props.values.filter((_, valueIndex) => valueIndex !== index)
		);

	return (
		<Space vertical style={{ width: '100%' }}>
			<div
				style={{
					display: 'grid',
					gridTemplateColumns: `repeat(${props.columns ?? 1}, minmax(0, 1fr))`,
					gap: 8
				}}
			>
				{props.values.map((value, index) => (
					<Space.Compact key={index} style={{ width: '100%' }}>
						<Input
							value={value}
							placeholder={props.placeholder}
							onChange={event => update(index, event.target.value)}
						/>
						<Button danger onClick={() => remove(index)}>
							Remove
						</Button>
					</Space.Compact>
				))}
			</div>
			<Button style={{ marginBottom: 8 }} onClick={add}>
				Add value
			</Button>
		</Space>
	);
}

function Config() {
	const [messageApi, contextHolder] = message.useMessage();
	const [rules, setRules] = useState<ClassificationRules>(emptyRules);
	const [loading, setLoading] = useState(true);
	const [editing, setEditing] = useState<'direct' | 'zip' | null>(null);
	const [draft, setDraft] = useState<string[]>([]);
	const [saving, setSaving] = useState(false);
	const [configuration, setConfiguration] = useState<Configuration | null>(
		null
	);
	const [mappingEditing, setMappingEditing] = useState<string | null>(null);
	const [mappingDraft, setMappingDraft] = useState<string[]>([]);
	const [conditionEditing, setConditionEditing] = useState(false);
	const [conditionDraft, setConditionDraft] = useState<MailableCondition[]>([]);

	const nurtureRef = useRef<InputRef>(null);

	useEffect(() => {
		window.pywebview?.api
			?.get_configuration()
			.then(configuration => {
				setConfiguration(configuration as Configuration);
				setRules(configuration.classification_rules);
			})
			.catch(error => messageApi.error(String(error)))
			.finally(() => setLoading(false));
	}, [messageApi]);

	const refreshConfiguration = async () => {
		const latest = await window.pywebview?.api?.get_configuration();
		if (latest) {
			setConfiguration(latest as Configuration);
			setRules(latest.classification_rules);
		}
		return latest as Configuration | undefined;
	};

	const openEditor = async (section: 'direct' | 'zip') => {
		try {
			const latestConfiguration = await refreshConfiguration();
			if (!latestConfiguration) return;
			const latest = latestConfiguration.classification_rules;
			setRules(latest);
			setDraft(
				section === 'direct'
					? [...latest.direct_applicant_types]
					: [...latest.ic_postal_prefixes]
			);
			setEditing(section);
		} catch (error) {
			messageApi.error(error instanceof Error ? error.message : String(error));
		}
	};

	const save = async () => {
		if (!editing) return;
		setSaving(true);
		try {
			const configuration = await window.pywebview?.api?.get_configuration();
			if (!configuration) return;
			const latest = configuration.classification_rules;
			const directApplicantTypes =
				editing === 'direct'
					? draft.map(value => value.trim()).filter(Boolean)
					: latest.direct_applicant_types;
			const icPostalPrefixes =
				editing === 'zip'
					? draft.map(value => value.trim().toUpperCase()).filter(Boolean)
					: latest.ic_postal_prefixes;
			const saved = await window.pywebview?.api?.update_configuration({
				...configuration,
				classification_rules: {
					direct_applicant_types: directApplicantTypes,
					ic_postal_prefixes: icPostalPrefixes
				}
			});
			if (saved) {
				setConfiguration(saved as Configuration);
				setRules(saved.classification_rules);
				messageApi.success(
					editing === 'direct'
						? 'Direct applicant types saved.'
						: 'IC ZIP prefixes saved.'
				);
				setEditing(null);
			}
		} catch (error) {
			messageApi.error(error instanceof Error ? error.message : String(error));
		} finally {
			setSaving(false);
		}
	};

	const openMappingEditor = async (field: string) => {
		const latest = await refreshConfiguration();
		if (!latest) return;
		setMappingEditing(field);
		setMappingDraft([...(latest.field_mapping[field] || [])]);
	};

	const saveMapping = async () => {
		if (!mappingEditing) return;
		setSaving(true);
		try {
			const latest = await refreshConfiguration();
			if (!latest) return;
			const saved = await window.pywebview?.api?.update_configuration({
				...latest,
				field_mapping: {
					...latest.field_mapping,
					[mappingEditing]: mappingDraft
						.map(value => value.trim())
						.filter(Boolean)
				}
			});
			if (saved) setConfiguration(saved as Configuration);
			setMappingEditing(null);
			messageApi.success('Field mapping saved.');
		} catch (error) {
			messageApi.error(error instanceof Error ? error.message : String(error));
		} finally {
			setSaving(false);
		}
	};

	const saveConditions = async () => {
		setSaving(true);
		try {
			const latest = await refreshConfiguration();
			if (!latest) return;
			const saved = await window.pywebview?.api?.update_configuration({
				...latest,
				mailable_conditions: conditionDraft
			});
			if (saved) setConfiguration(saved as Configuration);
			setConditionEditing(false);
			messageApi.success('Mailable conditions saved.');
		} catch (error) {
			messageApi.error(error instanceof Error ? error.message : String(error));
		} finally {
			setSaving(false);
		}
	};

	const updateCondition = (
		index: number,
		changes: Partial<MailableCondition>
	) => {
		setConditionDraft(current =>
			current.map((condition, conditionIndex) =>
				conditionIndex === index ? { ...condition, ...changes } : condition
			)
		);
	};

	const reset = async () => {
		if (!editing) return;
		const section =
			editing === 'direct' ? 'direct_applicant_types' : 'ic_postal_prefixes';
		setSaving(true);
		try {
			const resetRules =
				await window.pywebview?.api?.reset_classification_rule(section);
			if (resetRules) {
				setRules(resetRules);
				setDraft(
					editing === 'direct'
						? [...resetRules.direct_applicant_types]
						: [...resetRules.ic_postal_prefixes]
				);
				messageApi.success('Rules reset.');
			}
		} catch (error) {
			messageApi.error(error instanceof Error ? error.message : String(error));
		} finally {
			setSaving(false);
		}
	};

	const displayValues = (values: string[]) => (
		<Space wrap>
			{values.map(value => (
				<Tag key={value}>{value}</Tag>
			))}
		</Space>
	);

	return (
		<>
			{contextHolder}
			<Card
				title="Classification configuration"
				loading={loading}
				style={{ margin: 16, maxWidth: 760 }}
				extra={<Button onClick={() => window.history.back()}>Back</Button>}
			>
				<Typography.Paragraph type="secondary">
					These rules determine Direct/Non-direct and IC/OOC classification in
					the next report.
				</Typography.Paragraph>
				<Card
					title="Manual settings file"
					size="small"
					style={{ marginBottom: 16 }}
					extra={
						<Button
							onClick={() =>
								configuration &&
								window.pywebview?.api?.open_dir(configuration.settings_dir)
							}
							disabled={!configuration?.settings_path}
						>
							Open folder
						</Button>
					}
				>
					<Typography.Text code>
						{configuration?.settings_path || 'Loading...'}
					</Typography.Text>
					<Typography.Paragraph type="secondary" style={{ marginTop: 8 }}>
						You can edit this JSON file manually. Reopen or refresh this page to
						load the latest values.
					</Typography.Paragraph>
				</Card>
				<Card
					title="Direct applicant types"
					size="small"
					style={{ marginBottom: 16 }}
					extra={<Button onClick={() => openEditor('direct')}>Edit</Button>}
				>
					{displayValues(rules.direct_applicant_types)}
				</Card>
				<Card
					title="IC ZIP prefixes"
					size="small"
					extra={<Button onClick={() => openEditor('zip')}>Edit</Button>}
				>
					{displayValues(rules.ic_postal_prefixes)}
				</Card>
				<Card title="Mailable rules" size="small" style={{ marginBottom: 16 }}>
					<Space style={{ display: 'flex', justifyContent: 'space-between' }}>
						<Typography.Text strong>Conditions</Typography.Text>
						<Button
							size="small"
							onClick={async () => {
								const latest = await refreshConfiguration();
								if (latest) {
									setConditionDraft(
										latest.mailable_conditions.map(condition => ({
											...condition,
											values: [...condition.values]
										}))
									);
									setConditionEditing(true);
								}
							}}
						>
							Edit conditions
						</Button>
					</Space>
					{(configuration?.mailable_conditions || []).map(condition => (
						<Space
							key={condition.key}
							style={{ display: 'flex', margin: '8px 0' }}
						>
							<Switch checked={condition.enabled} disabled />
							<span>{condition.label}</span>
							<Tag>{condition.field}</Tag>
							<Tag>{condition.mode}</Tag>
						</Space>
					))}
					<Divider />
					<Typography.Paragraph type="secondary">
						Each condition can be enabled, renamed, pointed at a field, and
						configured with a matching mode and values.
					</Typography.Paragraph>
				</Card>
				<Card title="Field mapping" size="small">
					{Object.entries(configuration?.field_mapping || {}).map(
						([field, values]) => (
							<Space
								key={field}
								style={{
									display: 'flex',
									justifyContent: 'space-between',
									marginBottom: 8
								}}
							>
								<span>{field}</span>
								<Space>
									{values.map(value => (
										<Tag key={value}>{value}</Tag>
									))}
									<Button size="small" onClick={() => openMappingEditor(field)}>
										Edit
									</Button>
								</Space>
							</Space>
						)
					)}
				</Card>
				<Card title="Nurture list" size="small" style={{ marginTop: 16 }}>
					<Switch
						disabled={!configuration?.nurture?.file_path}
						checked={configuration?.nurture?.enable}
						onChange={async checked => {
							const saved = await window.pywebview?.api?.update_configuration({
								...configuration!,
								nurture: {
									...configuration!.nurture,
									report_field: checked
										? nurtureRef.current?.input?.value || 'Prospect Id'
										: 'Prospect Id',
									enable: checked
								}
							});
							if (saved) setConfiguration(saved as Configuration);
						}}
					/>
					<Typography.Paragraph type="secondary">
						People in this Excel list are excluded from Mailable only.
					</Typography.Paragraph>
					<Typography.Text code>
						{configuration?.nurture.file_path || 'No list selected'}
					</Typography.Text>
					<Space style={{ display: 'flex', marginTop: 12 }}>
						<Input
							ref={nurtureRef}
							defaultValue={'Prospect Id'}
							placeholder="Master Report: Prospect Id"
						/>
						<Button
							onClick={async () => {
								const selected =
									await window.pywebview?.api?.select_nurture_file();
								if (selected) {
									const latest = await refreshConfiguration();
									if (latest) {
										const saved =
											await window.pywebview?.api?.update_configuration({
												...latest,
												nurture: {
													...latest.nurture,
													file_path: selected.file_path,
													report_field: 'Prospect Id'
												}
											});
										if (saved) setConfiguration(saved as Configuration);
									}
								}
							}}
						>
							Upload Excel list
						</Button>
					</Space>
				</Card>
			</Card>
			<Drawer
				title="Edit Mailable conditions"
				placement="right"
				size={620}
				open={conditionEditing}
				onClose={() => setConditionEditing(false)}
				footer={
					<Button type="primary" onClick={saveConditions} loading={saving}>
						Save conditions
					</Button>
				}
			>
				<Space vertical style={{ width: '100%' }}>
					{conditionDraft.map((condition, index) => (
						<Card
							key={index}
							size="small"
							title={
								<Input
									value={condition.label}
									placeholder="Condition label"
									onChange={event =>
										updateCondition(index, { label: event.target.value })
									}
								/>
							}
							extra={
								<Button
									danger
									size="small"
									onClick={() =>
										setConditionDraft(current =>
											current.filter(
												(_, conditionIndex) => conditionIndex !== index
											)
										)
									}
								>
									Delete
								</Button>
							}
						>
							<Space vertical style={{ width: '100%' }}>
								<Switch
									checked={condition.enabled}
									onChange={enabled => updateCondition(index, { enabled })}
								/>
								<Input
									addonBefore="Key"
									value={condition.key}
									onChange={event =>
										updateCondition(index, { key: event.target.value })
									}
								/>
								<Input
									addonBefore="Field"
									value={condition.field}
									placeholder="Existing mapping key or Excel header"
									onChange={event =>
										updateCondition(index, { field: event.target.value })
									}
								/>
								<Select
									style={{ width: '100%' }}
									value={condition.mode}
									onChange={mode => updateCondition(index, { mode })}
									options={[
										{
											value: 'exclude_if_value',
											label: 'Exclude if value matches'
										},
										{ value: 'require_value', label: 'Require value to match' },
										{
											value: 'exclude_if_non_empty',
											label: 'Exclude if non-empty'
										},
										{ value: 'require_non_empty', label: 'Require non-empty' },
										{ value: 'exclude_if_empty', label: 'Exclude if empty' }
									]}
								/>
								<EditableValues
									values={condition.values}
									onChange={values => updateCondition(index, { values })}
									placeholder="Matching value"
								/>
							</Space>
						</Card>
					))}
					<Button
						onClick={() =>
							setConditionDraft(current => [
								...current,
								{
									key: `condition_${current.length + 1}`,
									label: 'New condition',
									field: '',
									mode: 'exclude_if_value',
									enabled: true,
									values: []
								}
							])
						}
					>
						Add condition
					</Button>
				</Space>
			</Drawer>
			<Drawer
				title={
					editing === 'direct'
						? 'Edit Direct applicant types'
						: 'Edit IC ZIP prefixes'
				}
				placement="right"
				size={520}
				open={editing !== null}
				onClose={() => setEditing(null)}
				footer={
					<Space>
						<Button onClick={reset} loading={saving}>
							Reset
						</Button>
						<Button type="primary" onClick={save} loading={saving}>
							Save
						</Button>
					</Space>
				}
			>
				<EditableValues
					values={draft}
					onChange={setDraft}
					placeholder={
						editing === 'direct'
							? 'Applicant Type treated as Direct'
							: 'For example, L4N'
					}
					columns={editing === 'zip' ? 3 : 1}
				/>
			</Drawer>
			<Drawer
				title={`Edit field mapping: ${mappingEditing || ''}`}
				placement="right"
				size={520}
				open={mappingEditing !== null}
				onClose={() => setMappingEditing(null)}
				footer={
					<Button type="primary" onClick={saveMapping} loading={saving}>
						Save
					</Button>
				}
			>
				<EditableValues
					values={mappingDraft}
					onChange={setMappingDraft}
					placeholder="Excel column header"
				/>
			</Drawer>
		</>
	);
}

