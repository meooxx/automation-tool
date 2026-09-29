import { createFileRoute } from '@tanstack/react-router';
import { Row, Col, message, DatePicker, Button, Form } from 'antd';
import PyUpload from '../components/PyUpload';
import { useState, useEffect, useTransition } from 'react';
import dayjs from 'dayjs';
export const Route = createFileRoute('/')({ component: Home });

declare global {
	interface Window {
		pywebview?: {
			api?: {
				bind_drop_event: (selector: string) => Promise<boolean>;
				unbind_drop_event: (selector: string) => Promise<boolean>;
				select_file: () => Promise<string | null>;
			};
		};
	}
}

function Home() {
	const [messageApi, contextHolder] = message.useMessage();
	const handleUploadSuccess = (filePath: string): void => {
		messageApi.success(`Choosed: ${filePath}`);
		setFilepath(filePath);
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
			await window.pywebview?.api?.process_file(
				curr?.format('YYYY-MM'),
				pre?.format('YYYY-MM')
			);
		});
	};

	useEffect(() => {
		if (curr == null) {
			setPre(undefined);
		} else {
			setPre(curr.subtract(1, 'month'));
		}
	}, [curr]);

	return (
		<>
			{contextHolder}
			<div>
				{contextHolder}
				<Row gutter={8}>
					<Col sm={12} lg={8}>
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
					</Col>
					<Col sm={12} lg={8}></Col>
					<Col sm={12} lg={8}></Col>
				</Row>
			</div>
		</>
	);
}

