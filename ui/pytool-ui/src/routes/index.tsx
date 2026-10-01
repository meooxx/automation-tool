import { createFileRoute } from '@tanstack/react-router';

import {
	Card,
	Row,
	Col,
	message,
	DatePicker,
	Button,
	Form,
} from 'antd';
import type { CardProps } from 'antd';

import PyUpload from '../components/PyUpload';
import PyLog from '../components/PyLog';
import { useState, useEffect, useTransition, useRef } from 'react';
import dayjs from 'dayjs';
import DirPicker from '../components/PyDirPicker';

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
				process_file: (curr: string, pre: string) => Promise<void>;
				ready: () => Promise<void>;
				open_dir: (path: string) => Promise<void>;
				get_output_dir: () => Promise<string>;
			};
		};
		CALL_METHODS?: Map<string, (a: any) => void>;
	}
}

function Home() {
	const [messageApi, contextHolder] = message.useMessage();
	const dirPickerRef = useRef<{ updateDir: () => void }>(null);
	const handleUploadSuccess = (filePath: string): void => {
		messageApi.success(`Choosed: ${filePath}`);
		setFilepath(filePath);
		dirPickerRef.current?.updateDir();
	};
	const [isPedding, startTransition] = useTransition();
	const [filepath, setFilepath] = useState<string | null>(null);
	const [curr, setCurr] = useState<dayjs.Dayjs | undefined>(dayjs());
	const [pre, setPre] = useState<dayjs.Dayjs | undefined>(
		dayjs().subtract(1, 'month')
	);
	const disabled = curr === null || filepath === null;
	const handleProcess = () => {
		startTransition(async () => {
			try {
				await window.pywebview?.api?.process_file(
					curr!.format('YYYY-MM'),
					pre
						? pre.format('YYYY-MM')
						: curr!.subtract(1, 'month').format('YYYY-MM')
				);
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
		window.pywebview?.api?.ready();
	}, []);
	const cardStyles: CardProps[styles] = {
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
								labelCol={{ span: 4 }}
								wrapperCol={{ span: 20 }}
								layout="horizontal"
								style={{ padding: '16px', width: '100%' }}
							>
								<Form.Item label="File" style={{ marginTop: '16px' }}>
									<PyUpload onSuccess={handleUploadSuccess}></PyUpload>
								</Form.Item>
								<Form.Item
									label="Month"

									style={{ marginTop: '16px' }}
								>
									<DatePicker
										defaultValue={dayjs(curr, 'YYYY-MM')}
										onChange={date => setCurr(date ? date : undefined)}
										style={{ width: '100%' }}
										picker="month"
									/>
								</Form.Item>
								<Form.Item label="Prior" style={{ marginTop: '16px' }}>
									<DatePicker
										maxDate={dayjs(curr).subtract(1, 'month')}
										disabled={pre == null && pre == null}
										value={pre}
										onChange={date => setPre(date ? date : undefined)}
										style={{ width: '100%' }}
										picker="month"
									></DatePicker>
								</Form.Item>

								<Form.Item
									wrapperCol={{ offset: 4 }}
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

