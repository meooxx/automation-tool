import { createFileRoute } from '@tanstack/react-router';
import {
	Card,
	Row,
	Col,
	message,
	DatePicker,
	Button,
	Form,
	Flex,
	Tooltip
} from 'antd';
import type { CardProps } from 'antd';

import PyUpload from '../components/PyUpload';
import PyLog from '../components/PyLog';
import { useState, useEffect, useTransition, useRef } from 'react';
import dayjs from 'dayjs';
import DirPicker from '../components/PyDirPicker';
import LogDir from '../components/LogDir';
import { SourceSelect, type Source } from '../components/SouceSelect';
import { InfoCircleOutlined } from '@ant-design/icons';
export const Route = createFileRoute('/')({ component: Home });

declare global {
	interface Window {
		pywebview?: {
			api?: {
				bind_drop_event: (selector: string) => Promise<boolean>;
				unbind_drop_event: (selector: string) => Promise<boolean>;
				// select_file: (filetype?: 'OPEN' | 'DIR') => Promise<string | null>;
				select_dir: (savedir?: boolean) => Promise<string | null>;
				get_file_path: () => Promise<string | null>;
				select_file: () => Promise<string | null>;
				select_file_and_get_lead_sources: () => Promise<{
					file_path: string;
					lead_sources: { key: string; text: string; aliases: string[] }[];
				} | null>;
				process_file: (
					curr: string,
					pre: string,
					selected?: string
				) => Promise<void>;

				ready: () => Promise<void>;
				open_dir: (path: string) => Promise<void>;
				open_path: (path: string) => Promise<void>;
				get_log_path: () => Promise<string | null>;
				get_output_dir: () => Promise<string>;
				save_source_headers: (sources: string) => Promise<void>;
				get_source_headers: () => Promise<Source[]>;
			};
		};
		CALL_METHODS?: Map<string, (a: any) => void>;
	}
}

function Home() {
	const [messageApi, contextHolder] = message.useMessage();
	const dirPickerRef = useRef<{ updateDir: () => void }>(null);
	const handleUploadSuccess = async (data: {
		file_path: string;
		lead_sources: { text: string }[];
	}): Promise<void> => {
		messageApi.success(`Choosed: ${data.file_path}`);
		setFilepath(data.file_path);
		const map = new Map<string, Source>();
		selectedSources.forEach(source => {
			map.set(source.value, source);
		});
		const newSources = data.lead_sources.map(item => {
			if (map.has(item.text)) {
				const s = map.get(item.text)!;
				map.delete(item.text);
				return s;
			}
			return {
				key: item.text,
				label: item.text,
				value: item.text,
				alias: [item.text],
				columnName: item.text
			};
		});
		if (map.size > 0) {
			newSources.push(...Array.from(map.values()));
		}
		setLeadSources(newSources);
		dirPickerRef.current?.updateDir();
	};
	const [isPedding, startTransition] = useTransition();
	const [filepath, setFilepath] = useState<string | null>(null);
	const [leadSources, setLeadSources] = useState<Source[]>([]);
	const [selectedSources, setSelectedSources] = useState<Source[]>([]);
	const [curr, setCurr] = useState<dayjs.Dayjs | undefined>(dayjs());
	const [pre, setPre] = useState<dayjs.Dayjs | undefined>(
		dayjs().subtract(1, 'month')
	);
	const disabled = curr === null || filepath === null || selectedSources.length === 0;
	const handleSelectedSourcesChange = (
		_: string,
		options?: Source | Source[]
	) => {
		if (!Array.isArray(options)) return;
		setSelectedSources(
			options.map(option => ({
				value: option.value,
				label: option.label,
				key: option.key,
				alias: option.alias,
				columnName: option.columnName
			}))
		);
	};
	// const handleSaveAdvancedSources = (sources: Source[]) => {
	// 	setSelectedSources(sources);
	// };
	const handleProcess = () => {
		startTransition(async () => {
			try {
				await window.pywebview?.api?.process_file(
					curr!.format('YYYY-MM'),
					pre
						? pre.format('YYYY-MM')
						: curr!.subtract(1, 'month').format('YYYY-MM'),
					JSON.stringify(selectedSources)
				);
				messageApi.success('Process completed successfully.');
			} catch (e) {
				messageApi.error(e instanceof Error ? e.message : String(e));
			}
		});
	};

	useEffect(() => {
		if (curr == null) {
			setPre(undefined);
		} else {
			setPre(curr.subtract(1, 'month'));
		}
	}, [curr]);
	useEffect(() => {
		window.pywebview?.api?.get_source_headers().then((sources: Source[]) => {
			if (sources?.length > 0) {
				setSelectedSources(
					sources.map(source => ({
						value: source.value,
						label: source.label,
						key: source.key,
						alias: source.alias,
						columnName: source.columnName
					}))
				);
			}
		});
	}, []);
	const cardStyles: CardProps['styles'] = {
		body: {
			flexGrow: 1
		}
	};

	return (
		<>
			{contextHolder}
			<div style={{ padding: '16px', width: '100%' }}>
				<Row gutter={8}>
					<Col sm={12} lg={12}>
						<Card>
							<Form
								initialValues={{
									month: dayjs(curr)
								}}
								// form={form}
								labelCol={{ span: 5 }}
								wrapperCol={{ span: 20 }}
								layout="horizontal"
								style={{ padding: '16px', width: '100%' }}
							>
								<Form.Item label="File" style={{ marginTop: '16px' }}>
									<PyUpload
										onChange={(path?: string) => setFilepath(path || null)}
										onSuccess={handleUploadSuccess}
									></PyUpload>
								</Form.Item>
								<Form.Item
									label="Month"
									name="month"
									rules={[{ required: true, message: 'Please select a month' }]}
									style={{ marginTop: '16px' }}
								>
									<DatePicker
										maxDate={dayjs()}
										minDate={dayjs('2020-01')}
										// defaultValue={dayjs(curr, 'YYYY-MM')}
										onChange={date => setCurr(date ? date : undefined)}
										style={{ width: '100%' }}
										picker="month"
									/>
								</Form.Item>

								<Form.Item label="Prior" style={{ marginTop: '16px' }}>
									<DatePicker
										maxDate={dayjs(curr).subtract(1, 'month')}
										disabled={curr == null}
										value={pre}
										onChange={date => setPre(date ? date : undefined)}
										style={{ width: '100%' }}
										picker="month"
									></DatePicker>
								</Form.Item>
								<Form.Item
									name="sources"
									rules={[
										() => ({
											validator(_) {
												if (selectedSources.length > 0) {
													return Promise.resolve();
												}
												return Promise.reject(
													new Error('Please select at least one source.')
												);
											}
										})
									]}
									label={
										<Tooltip title="you can then sort or aggregate several sources to one column using adv button. for example, you can use 'careermatch' to include 'careermatch' and 'career-match' to one source.">
											Src
											<InfoCircleOutlined style={{ marginLeft: '4px' }} />
										</Tooltip>
									}
								>
									<SourceSelect
										disabled={leadSources.length === 0}
										sources={selectedSources}
										onChange={handleSelectedSourcesChange}
										options={leadSources}
										// onOk={handleSaveAdvancedSources}
									/>
								</Form.Item>
								<Form.Item
									wrapperCol={{ offset: 5 }}
									style={{ marginTop: '16px' }}
								>
									<Button
										disabled={disabled}
										type="primary"
										onClick={handleProcess}
										loading={isPedding}
									>
										Process
									</Button>
								</Form.Item>
							</Form>
						</Card>
					</Col>
					<Col sm={12} lg={12}>
						<Card
							actions={[
								<Flex vertical gap={4}>
									<DirPicker
										ref={dirPickerRef}
										onSuccess={dir => {
											messageApi.success(`Output dir: ${dir}`);
										}}
										onError={e => {
											messageApi.error(
												e instanceof Error ? e.message : String(e)
											);
										}}
									/>

									<LogDir />
								</Flex>
							]}
							title="Run Logs"
							styles={cardStyles}
							style={{
								height: '100%',
								width: '100%',
								display: 'flex',
								flexDirection: 'column'
							}}
						>
							<PyLog />
						</Card>
					</Col>
				</Row>
			</div>
		</>
	);
}
