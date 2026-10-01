import { Row, Col, Input, Button, Tooltip } from 'antd';
import { useState, useEffect, useImperativeHandle } from 'react';

interface DirPickerProps {
	onError?: (error: Error) => void;
	onSuccess?: (dir: string) => void;
	ref?: React.Ref<{ updateDir: () => void }>;
}

export default function DirPicker(props: DirPickerProps) {
	const [dir, setPath] = useState<string>();
	useImperativeHandle(
		props.ref,
		() => ({
			updateDir: () => {
				getOutDir();
			}
		}),
		[]
	);
	const handleChooseOutdir = async () => {
		const dir = await window.pywebview?.api?.select_dir(true);
		if (dir) {
			setPath(dir);
			props.onSuccess?.(dir);
		}
	};
	const getOutDir = async () => {
		const dir = await window.pywebview?.api?.get_output_dir().catch(e => {
			props.onError?.(e);
		});
		if (dir) setPath(dir!);
	};
	useEffect(() => {
		getOutDir();
	}, []);

	return (
		<Row gutter={8} align="middle">
			<Col offset={1}>outdir:</Col>
			<Col>
				<Tooltip placement="leftTop" title={dir}>
					<Input
						value={dir}
						readOnly
						defaultValue="Same as the file by default"
					/>
				</Tooltip>
			</Col>
			<Col>
				<Button type="primary" onClick={handleChooseOutdir}>
					change
				</Button>
			</Col>
		</Row>
	);
}

