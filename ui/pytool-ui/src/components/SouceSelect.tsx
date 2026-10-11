import {
	Button,
	Select,
	Row,
	Col,
	Modal,
	Form,
	Input,
	type ModalProps,
	Typography
} from 'antd';
import { createContext, useState, useMemo, useContext } from 'react';
import type {
	DragEndEvent,
	DraggableAttributes,
	DraggableSyntheticListeners
} from '@dnd-kit/core';
import {
	DndContext,
	PointerSensor,
	useSensor,
	useSensors
} from '@dnd-kit/core';
import { restrictToVerticalAxis } from '@dnd-kit/modifiers';
import {
	SortableContext,
	useSortable,
	verticalListSortingStrategy
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { HolderOutlined } from '@ant-design/icons';
import type { FC } from 'react';
import { useTransition } from 'react';
interface RowContextProps {
	setActivatorNodeRef?: (element: HTMLElement | null) => void;
	listeners?: DraggableSyntheticListeners;
	attributes?: DraggableAttributes;
}

const RowContext = createContext<RowContextProps>({});

const DragHandle: FC = () => {
	const { setActivatorNodeRef, listeners, attributes } = useContext(RowContext);
	return (
		<Button
			type="text"
			size="small"
			icon={<HolderOutlined />}
			style={{ cursor: 'move' }}
			ref={setActivatorNodeRef}
			{...attributes}
			{...listeners}
		/>
	);
};

interface SortableItemProps {
	id: number;
	children?: React.ReactNode;
}

const SortableItem: React.FC<SortableItemProps> = ({ id, children }) => {
	const {
		setNodeRef,
		setActivatorNodeRef,
		attributes,
		listeners,
		transform,
		transition,
		isDragging
	} = useSortable({ id });

	const style: React.CSSProperties = {
		transform: CSS.Translate.toString(transform),
		transition,
		...(isDragging ? { position: 'relative', zIndex: 9999 } : {})
	};

	const contextValue = useMemo<RowContextProps>(
		() => ({ setActivatorNodeRef, listeners, attributes }),
		[setActivatorNodeRef, listeners, attributes]
	);

	return (
		<RowContext.Provider value={contextValue}>
			<div ref={setNodeRef} style={style}>
				{children}
			</div>
		</RowContext.Provider>
	);
};

export type Source = {
	value: string;
	label: string;
	key: string;
	alias: string[];
	columnName: string;
};
export function SourceSelect(props: {
	disabled?: boolean;
	sources: Source[];
	options: Source[];
	onOk?: (Sources: Source[]) => void;
	onChange?: (v: string, options?: Source | Source[]) => void;
}) {
	const [open, setOpen] = useState(false);
	const [form] = Form.useForm<{ sources: Source[] }>();
	const [isPending, startTransition] = useTransition();
	const sensors = useSensors(
		useSensor(PointerSensor, { activationConstraint: { distance: 1 } })
	);
	const styleFn: ModalProps['styles'] = () => ({
		body: {
			padding: 16,
			maxHeight: '350px',
			overflowY: 'auto'
		}
	});
	const handleOk = async () => {
		startTransition(async () => {
			const values = form.getFieldsValue().sources || [];
			props.onOk?.(values);
			await window.pywebview?.api?.save_source_headers(JSON.stringify(values));
			setOpen(false);
		});
	};
	const handleOpenModal = (b: boolean) => {
		if (b) {
			form.setFieldsValue({
				sources: props.sources.map(source => ({
					value: source.value,
					label: source.label,
					key: source.value,
					columnName: source.columnName,
					alias: source.alias
				}))
			});
		}
	};

	return (
		<>
			<Modal
				loading={isPending}
				title={
					<>
						<Typography.Title level={5}>
							Advanced Source Mapping
						</Typography.Title>
						<Typography.Text type="secondary">
							you can sort or rename columns(left) in the report aggregate
							them(right) to a single source. for example, you can map
							'career-match' and 'careermatch' to 'careermatch'
						</Typography.Text>
					</>
				}
				open={open}
				onOk={handleOk}
				afterOpenChange={handleOpenModal}
				onCancel={() => setOpen(false)}
				width={700}
				styles={styleFn}
				scrollLock={true}
				destroyOnHidden={false}
				modalRender={dom => {
					return (
						<Form<{ sources: Source[] }>
							layout="vertical"
							form={form}
							name="form_in_modal"
							preserve={true}
							clearOnDestroy={false}
						>
							{dom}
						</Form>
					);
				}}
			>
				<Form.List name="sources">
					{(fields, { move }) => {
						const onDragEnd = ({ active, over }: DragEndEvent) => {
							if (over && active.id !== over.id) {
								const activeIndex = fields.findIndex(
									field => field.key === active.id
								);
								const overIndex = fields.findIndex(
									field => field.key === over.id
								);
								if (activeIndex !== -1 && overIndex !== -1) {
									move(activeIndex, overIndex);
									console.log('move', activeIndex, overIndex);
								}
							}
						};

						return (
							<DndContext
								sensors={sensors}
								modifiers={[restrictToVerticalAxis]}
								onDragEnd={onDragEnd}
							>
								<SortableContext
									items={fields.map(field => field.key)}
									strategy={verticalListSortingStrategy}
								>
									{fields.map(({ key, name, ...restField }) => (
										<SortableItem key={key} id={key}>
											<Form.Item noStyle name={[name, 'label']}></Form.Item>
											<Form.Item noStyle name={[name, 'value']}></Form.Item>
											<Form.Item noStyle name={[name, 'key']}></Form.Item>

											<Row
												gutter={8}
												align="middle"
												style={{ marginBottom: '18px' }}
											>
												<Col span={2}>
													<DragHandle />
												</Col>
												<Col span={11}>
													<Form.Item
														{...restField}
														name={[name, 'columnName']}
														rules={[
															{
																required: true,
																message: 'name in report is required'
															}
														]}
													>
														<Input placeholder="column name in report" />
													</Form.Item>
												</Col>
												<Col span={11}>
													<Form.Item
														name={[name, 'alias']}
														rules={[
															{
																required: true,
																message: 'Missing a lead source'
															}
														]}
													>
														<Select
															style={{ width: '100%' }}
															options={props.options}
															mode="multiple"
															showSearch
															// items={1}
															placeholder="lead source"
														/>
													</Form.Item>
												</Col>
											</Row>
										</SortableItem>
									))}
								</SortableContext>
							</DndContext>
						);
					}}
				</Form.List>
			</Modal>
			<Row align="middle" justify="space-between">
				<Col span={20}>
					<Select
						value={props.sources.map(source => source.value)}
						mode="multiple"
						showSearch
						placeholder="Please select sources"
						style={{ width: '100%' }}
						onChange={props.onChange}
						options={props.options}
						disabled={props.disabled}
					></Select>
				</Col>

				<Col span={3}>
					<Button
						disabled={props.sources.length === 0 || props.disabled}
						onClick={() => setOpen(true)}
						type="default"
					>
						adv
					</Button>
				</Col>
			</Row>
		</>
	);
}

